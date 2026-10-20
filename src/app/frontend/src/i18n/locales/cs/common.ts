import type en from "../en/common";

const common: typeof en = {
  nav: {
    label: "Hlavní navigace",
    translate: "Překlad",
    requests: "Moje požadavky",
    dashboard: "Přehled",
    signOut: "Odhlásit se",
    back: "Zpět",
    account: "Účet a nastavení",
  },
  routes: {
    login: "Přihlášení",
    changePassword: "Změna hesla",
    translate: "Přeložit .srt",
    requests: "Moje požadavky",
    dashboard: "Přehled",
    editor: "Export a formátování",
    job: "Překládání",
    editorSubtitle: "Editor subt-ai-tles",
  },
  locale: {
    auto: "Automaticky (podle prohlížeče)",
    setting: "Jazyk",
    flag: "Jazyk: {name}",
    label: "Jazyk",
    names: { en: "English", cs: "Čeština" },
  },
  time: {
    hours: "{n} h",
    minutes: "{n} min",
    seconds: "{n} s",
    today: "Dnes, {time}",
    yesterday: "Včera, {time}",
  },
  loading: "Načítání…",
  retry: "Zkusit znovu",
  status: {
    ready: "Hotovo",
    processing: "Zpracovává se",
    failed: "Selhalo",
  },
  cues: "{count} titulek | {count} titulky | {count} titulků",
};

export default common;
