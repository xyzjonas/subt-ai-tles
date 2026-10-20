import type en from "../en/translate";

const translate: typeof en = {
  hero: {
    title: "Překládejte titulky pomocí AI",
    lead: "Nahrajte libovolný soubor .srt, vyberte jazyky a nechte jazykové modely vytvořit kontextové a synchronizované překlady.",
  },
  file: {
    label: "Zdrojový soubor s titulky",
    reading: "Načítání souboru…",
    prompt: "Klepněte pro výběr nebo přetáhněte soubor .srt",
    hint: "Soubory .srt v kódování UTF-8 do {max} MB",
    browse: "Vybrat ze zařízení",
    remove: "Odebrat soubor",
    cueCount: "{count} titulek s dialogem | {count} titulky s dialogem | {count} titulků s dialogem",
    validated: "UTF-8 ověřeno",
    encodingOk: "Kódování: v pořádku",
    unreadable: "Soubor se nepodařilo načíst.",
    noTimestamps: "Nebyly nalezeny žádné platné časové značky SRT.",
    size: { kb: "{n} KB", mb: "{n} MB" },
  },
  target: "Cílový jazyk",
  action: {
    start: "Přeložit titulky (LLM)",
    starting: "Spouštění…",
    startFailed: "Překlad se nepodařilo spustit",
    estimate: "Odhad zpracování: {value}",
    seconds: "~{n} s",
    tokens: "~{n} tokenů",
  },
  recent: {
    title: "Nedávné úlohy s titulky",
    viewAll: "Zobrazit vše",
  },
};

export default translate;
