export function renderTemplate(template: string, vars: Record<string, string | number | undefined>) {
  return template.replace(/\{\{\s*([a-zA-Z0-9_\.]+)\s*\}\}/g, (_m, key) => {
    const val = vars[key];
    return (val === undefined || val === null) ? '' : String(val);
  });
}




