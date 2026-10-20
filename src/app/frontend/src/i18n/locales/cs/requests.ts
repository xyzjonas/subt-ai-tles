import type en from "../en/requests";

const requests: typeof en = {
  title: "Historie překladů",
  tasks: "{count} úloha | {count} úlohy | {count} úloh",
  lead: "Prohlížejte, sledujte a exportujte překlady.",
  search: {
    placeholder: "Hledat soubory nebo jazyky...",
    label: "Hledat v překladech",
  },
  tabs: {
    label: "Stav překladu",
    processing: "Zpracovává se ({count})",
    completed: "Dokončeno ({count})",
  },
  empty: {
    processing: "Žádné překlady ve zpracování.",
    completed: "Žádné dokončené překlady.",
    processingSearch: "Hledání neodpovídají žádné překlady ve zpracování.",
    completedSearch: "Hledání neodpovídají žádné dokončené překlady.",
  },
  card: {
    open: "Otevřít {name}",
    processing: "Zpracovává se {percent} % • {done} / {total} řádků",
    percentLabel: "Přeloženo {percent} %",
    completed:
      "Dokončeno • {count} řádek | Dokončeno • {count} řádky | Dokončeno • {count} řádků",
    syncedWith: "Přeloženo modelem {model}",
    download: "Stáhnout",
    preparing: "Příprava…",
  },
};

export default requests;
