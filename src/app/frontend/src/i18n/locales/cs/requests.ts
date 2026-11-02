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
    archived: "Archiv ({count})",
  },
  empty: {
    processing: "Žádné překlady ve zpracování.",
    completed: "Žádné dokončené překlady.",
    archived: "Archiv je prázdný.",
    processingSearch: "Hledání neodpovídají žádné překlady ve zpracování.",
    completedSearch: "Hledání neodpovídají žádné dokončené překlady.",
    archivedSearch: "Hledání neodpovídají žádné archivované překlady.",
  },
  folder: {
    add: "Přidat do složky",
    moveTo: "Přesunout do složky",
    remove: "Odebrat ze složky",
    ungrouped: "Mimo složky",
    newPlaceholder: "Nová složka…",
    newLabel: "Název nové složky",
    create: "Vytvořit složku",
    rename: "Přejmenovat složku",
    renameLabel: "Název složky",
    delete: "Smazat složku (překlady zůstanou)",
    emptyHint: "Přetáhněte sem překlady nebo použijte „Přidat do složky“.",
  },
  archive: {
    action: "Archivovat",
    restore: "Obnovit",
    lead: "Archivované překlady jsou skryté v historii, ale stále je můžete otevřít a stáhnout.",
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
