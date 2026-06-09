import { useRef } from 'react';
import { Icon } from './Icon';
import { ingestCsv, fetchTemplate } from '../api/client';

interface Props {
  kind: 'ap' | 'ar-invoices' | 'ar-deposits';
  templateKind: string;
  label: string;
  toast: (title: string, sub: string, tone?: string) => void;
  onDone: () => void;
}

export function CsvImport({ kind, templateKind, label, toast, onDone }: Props) {
  const ref = useRef<HTMLInputElement>(null);

  async function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    e.target.value = '';
    if (!f) return;
    const text = await f.text();
    const r = await ingestCsv(kind, text);
    if (r) { toast('Imported', `${label} · ${r.ingested} rows · queue rebuilt`); onDone(); }
    else { toast('Import failed', 'Check the CSV matches the template', 'warn'); }
  }

  async function download() {
    const t = await fetchTemplate(templateKind);
    if (!t) { toast('Unavailable', 'Start the API to download templates', 'warn'); return; }
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([t], { type: 'text/csv' }));
    a.download = `${templateKind}-template.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  return (
    <span className="hstack" style={{ gap: 8 }}>
      <button className="btn btn-quiet btn-sm" onClick={download}><Icon name="download" size={14} /> Template</button>
      <button className="btn btn-quiet btn-sm" onClick={() => ref.current?.click()}><Icon name="file" size={14} /> Import {label}</button>
      <input ref={ref} type="file" accept=".csv,text/csv" style={{ display: 'none' }} onChange={onFile} />
    </span>
  );
}
