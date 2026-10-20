import type en from "../en/auth";

const auth: typeof en = {
  login: {
    title: "Přihlášení",
    lead: "pro pokračování do subt-ai-tles",
    username: "Uživatelské jméno",
    password: "Heslo",
    submit: "Přihlásit se",
    submitting: "Přihlašování…",
    failed: "Přihlášení se nezdařilo. Zkuste to prosím znovu.",
  },
  changePassword: {
    title: "Zvolte si nové heslo",
    lead: "Vaše heslo nastavil správce. Pro pokračování si zvolte vlastní.",
    temporary: "Dočasné heslo",
    next: "Nové heslo",
    hint: "Alespoň {min} znaků.",
    repeat: "Nové heslo znovu",
    mismatch: "Hesla se neshodují.",
    submit: "Změnit heslo",
    submitting: "Ukládání…",
    failed: "Heslo se nepodařilo změnit. Zkuste to prosím znovu.",
    signOut: "Odhlásit se",
  },
};

export default auth;
