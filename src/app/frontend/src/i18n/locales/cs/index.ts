import type en from "../en";
import auth from "./auth";
import common from "./common";
import dashboard from "./dashboard";
import editor from "./editor";
import errors from "./errors";
import progress from "./progress";
import requests from "./requests";
import translate from "./translate";
import users from "./users";

const cs: typeof en = { ...common, auth, dashboard, editor, errors, progress, requests, translate, users };

export default cs;
