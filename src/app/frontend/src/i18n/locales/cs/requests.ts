import type en from "../en/requests";

const requests: typeof en = {
  title: "Historie překladů",
  tasks: "{count} úloha | {count} úlohy | {count} úloh",
  lead: "Prohlížejte, sledujte a exportujte úlohy s titulky.",
  search: { placeholder: "Hledat soubory nebo jazyky...", label: "Hledat v požadavcích" },
  tabs: { label: "Stav požadavku", processing: "Zpracovává se ({count})", completed: "Dokončeno ({count})" },
  empty: {
    processing: "Žádné požadavky ve zpracování.",
    completed: "Žádné dokončené požadavky.",
    processingSearch: "Hledání neodpovídají žádné požadavky ve zpracování.",
    completedSearch: "Hledání neodpovídají žádné dokončené požadavky.",
  },
  card: {
    open: "Otevřít {name}",
    processing: "Zpracovává se {percent} % • {done} / {total} řádků",
    percentLabel: "Přeloženo {percent} %",
    completed: "Dokončeno • {count} řádek | Dokončeno • {count} řádky | Dokončeno • {count} řádků",
    syncedWith: "Synchronizováno modelem {model}",
    download: "Stáhnout",
    preparing: "Příprava…",
  },
};

export default requests;
