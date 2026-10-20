import type en from "../en/progress";

const progress: typeof en = {
  loadFailed: "Tento požadavek se nepodařilo načíst.",
  failedFallback: "Tento překlad selhal.",
  confirmCancel: "Zrušit tento překlad? Již spotřebované tokeny se i tak účtují.",
  stage: {
    recognizing: "Rozpoznávání titulu…",
    summarizing: "Shrnování děje…",
    translating: "Překládání titulků {done}/{total}",
  },
  overview: {
    label: "Přehled úlohy",
    live: "Živě",
    specs: "SubRip (.srt) • UTF-8 • Odesláno {ago}",
  },
  stream: {
    title: "Živý překlad",
    cue: "Titulek č. {index}",
    waiting: "Čekání na první přeložený řádek…",
    duration: "délka {seconds} s",
  },
  milestones: {
    title: "Průběh",
    steps: "{count} krok | {count} kroky | {count} kroků",
    state: { done: "Hotovo", active: "Zpracovává se", pending: "Čeká", skipped: "Přeskočeno" },
    recognize: {
      title: "Nahrání a rozpoznání",
      active: "Čtení souboru a vyhledávání titulu…",
      skipped: "Titul nebyl rozpoznán",
      done: "Titul rozpoznán",
    },
    summarize: {
      title: "Shrnutí",
      pending: "Čeká na vyhledání titulu",
      active: "Čtení celého scénáře pro získání kontextu…",
      generated: "Shrnutí děje vytvořeno",
      stored: "Použito uložené shrnutí děje",
      skipped: "Titul nebyl rozpoznán, shrnutí není potřeba",
        },
    translate: {
      title: "Překlad titulků",
      done: "Přeloženo všech {total} řádků",
      active: "Překládání řádků {from}–{to} z {total}…",
      pending: "Čeká na shrnutí děje",
    },
    finish: { title: "Hotovo", done: "Připraveno ke kontrole", pending: "Čeká na překlad" },
  },
  gauge: {
    label: "Průběh překladu",
    lines: "{processed} / {total} řádků",
    tagline: "Překlad nuancí dialogů",
    note: "Zohledňování kontextu, hovorových výrazů a synchronizace časování…",
    chunk: "Průběh aktuálního úseku",
  },
  controls: {
    notify: "Upozornit po dokončení",
    notifyHint: "Po dokončení překladu odeslat push oznámení",
    cancel: "Zrušit překlad",
    cancelling: "Rušení…",
    foot: "Dosud spotřebované tokeny se i tak účtují",
  },
};

export default progress;
