import type en from "../en/membership";

const membership: typeof en = {
  form: {
    title: "Požádat o účet",
    lead: "Řekněte nám, kdo jste. Každou žádost ručně posuzuje správce.",
    email: "E-mail",
    details: "Chcete nám ještě něco sdělit? (nepovinné)",
    detailsHint: "Například k čemu chcete subt-ai-tles používat.",
    submit: "Odeslat žádost",
    submitting: "Odesílání…",
    failed: "Žádost se nepodařilo odeslat. Zkuste to prosím znovu.",
    invalidEmail: "Zadejte platnou e-mailovou adresu (nejvýše {max} znaků).",
    backToLogin: "Zpět na přihlášení",
  },
  sent: {
    title: "Žádost přijata",
    lead: "Děkujeme! Jakmile ji správce schválí, pošle vám přihlašovací údaje.",
  },
  admin: {
    loadFailed: "Žádosti o členství se nepodařilo načíst.",
    actionFailed: "Žádost se nepodařilo upravit.",
    intro: "Lidé, kteří požádali o účet. Schválením se vytvoří uživatel s výchozí kvótou.",
    filter: "Stav žádosti",
    status: { pending: "Čeká", approved: "Schváleno", rejected: "Zamítnuto" },
    empty: { pending: "Žádné žádosti nečekají.", approved: "Žádné schválené žádosti.", rejected: "Žádné zamítnuté žádosti." },
    received: "Přijato {date}",
    noDetails: "Bez doplňujících údajů.",
    approve: "Schválit",
    reject: "Zamítnout",
    rejecting: "Zamítání…",
    approveTitle: "Schválit {email}",
    temporary: "Dočasné heslo",
    confirm: "Vytvořit uživatele",
    confirming: "Vytváření…",
    cancel: "Zrušit",
    approved: "Uživatel vytvořen",
    share: "Předejte tyto údaje uživateli {username}. Při prvním přihlášení si zvolí nové heslo a toto heslo se již nezobrazí.",
    username: "Uživatelské jméno",
    done: "Hotovo",
  },
};

export default membership;
