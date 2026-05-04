import * as vscode from 'vscode';
import * as http from 'http';
import * as https from 'https';
import { URL } from 'url';

interface TranscribeResponse {
    text: string;
    lang: string;
    mode?: string;
    output: string;
}

function postJson<T>(url: string, body: object): Promise<T> {
    return new Promise((resolve, reject) => {
        const u = new URL(url);
        const lib = u.protocol === 'https:' ? https : http;
        const data = JSON.stringify(body);
        const req = lib.request(
            {
                hostname: u.hostname,
                port: u.port,
                path: u.pathname,
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) },
            },
            res => {
                let chunks = '';
                res.on('data', c => (chunks += c));
                res.on('end', () => {
                    try {
                        const parsed = JSON.parse(chunks);
                        if (res.statusCode && res.statusCode >= 400) {
                            reject(new Error(parsed.detail || `HTTP ${res.statusCode}`));
                        } else {
                            resolve(parsed as T);
                        }
                    } catch (e) {
                        reject(e);
                    }
                });
            }
        );
        req.on('error', reject);
        req.write(data);
        req.end();
    });
}

async function transcribeText(text: string, lang: string, mode?: string): Promise<string> {
    const cfg = vscode.workspace.getConfiguration('hunmin');
    const url = cfg.get<string>('serverUrl', 'http://localhost:8000') + '/transcribe';
    const r = await postJson<TranscribeResponse>(url, { text, lang, mode });
    return r.output;
}

async function reverseText(text: string, system: string = 'rr'): Promise<string> {
    const cfg = vscode.workspace.getConfiguration('hunmin');
    const url = cfg.get<string>('serverUrl', 'http://localhost:8000') + '/reverse';
    const r = await postJson<{ text: string; system: string; output: string }>(url, { text, system });
    return r.output;
}

async function pickLang(): Promise<string | undefined> {
    const cfg = vscode.workspace.getConfiguration('hunmin');
    const def = cfg.get<string>('defaultLang', 'en');
    const langs = ['en','es','it','de','ru','fr','pt','nl','pl','tr','id','hu','sk','cs','ro',
                   'hr','sr','mk','vi','fa','hi','ar','el','he','th','ja','zh','ko'];
    return await vscode.window.showQuickPick(
        langs.map(l => ({ label: l, description: l === def ? '(default)' : '' })),
        { placeHolder: 'Source language' }
    ).then(p => p?.label);
}

export function activate(context: vscode.ExtensionContext) {
    // 1. Transcribe selection
    context.subscriptions.push(
        vscode.commands.registerCommand('hunmin.transcribeSelection', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor || editor.selection.isEmpty) return;
            const text = editor.document.getText(editor.selection);
            const lang = await pickLang();
            if (!lang) return;
            try {
                const out = await transcribeText(text, lang);
                editor.edit(eb => eb.replace(editor.selection, out));
            } catch (e: any) {
                vscode.window.showErrorMessage(`Hunmin error: ${e.message}\n\nIs the server running?\n  uvicorn hunmin.server:app`);
            }
        })
    );

    // 2. UHPS-full
    context.subscriptions.push(
        vscode.commands.registerCommand('hunmin.transcribeSelectionUhpsFull', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor || editor.selection.isEmpty) return;
            const text = editor.document.getText(editor.selection);
            const lang = await pickLang();
            if (!lang) return;
            try {
                const out = await transcribeText(text, lang, 'uhps_full');
                editor.edit(eb => eb.replace(editor.selection, out));
            } catch (e: any) {
                vscode.window.showErrorMessage(`Hunmin error: ${e.message}`);
            }
        })
    );

    // 3. Reverse romanize
    context.subscriptions.push(
        vscode.commands.registerCommand('hunmin.reverseRomanize', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor || editor.selection.isEmpty) return;
            const text = editor.document.getText(editor.selection);
            try {
                const out = await reverseText(text, 'rr');
                editor.edit(eb => eb.replace(editor.selection, out));
            } catch (e: any) {
                vscode.window.showErrorMessage(`Hunmin error: ${e.message}`);
            }
        })
    );

    // 4. Show views (output panel)
    context.subscriptions.push(
        vscode.commands.registerCommand('hunmin.showViews', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor || editor.selection.isEmpty) return;
            const text = editor.document.getText(editor.selection);
            const lang = await pickLang();
            if (!lang) return;
            const cfg = vscode.workspace.getConfiguration('hunmin');
            const url = cfg.get<string>('serverUrl', 'http://localhost:8000') + '/views';
            try {
                const r = await postJson<Record<string, string>>(url, { text, lang });
                const panel = vscode.window.createOutputChannel('Hunmin');
                panel.clear();
                for (const [k, v] of Object.entries(r)) {
                    panel.appendLine(`${k.padEnd(12)} ${v ?? ''}`);
                }
                panel.show();
            } catch (e: any) {
                vscode.window.showErrorMessage(`Hunmin error: ${e.message}`);
            }
        })
    );
}

export function deactivate() {}
