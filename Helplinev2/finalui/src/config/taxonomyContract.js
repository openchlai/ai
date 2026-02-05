/**
 * Environment & Taxonomy Registry
 * This registry contains all configuration variables (Endpoints, VOIP, Taxonomy Roots) 
 * for different countries and deployment environments.
 */

export const ENVIRONMENT_REGISTRY = {
    // --- TANZANIA CONFIG (Production / Infrastructure) ---
    'TZ': {
        COUNTRY_NAME: "Tanzania",
        COUNTRY_CODE: "255",
        ENDPOINTS: {
            API_BASE: "/api-proxy",
            BACKEND_URL: "https://helpline.sematanzania.org",
            BACKEND_PATH: "/hh19jan2026",
            GATEWAY_AUTH: "https://helpline.sematanzania.org/v1/token/",
            GATEWAY_SEND_MSG: "https://helpline.sematanzania.org/v1/chat/",
            AMI_HOST: "wss://helpline.sematanzania.org:8384/ami/sync",
            ATI_HOST: "wss://helpline.sematanzania.org:8384/ati/sync",
            // Dev Proxy Targets (used by vite.config.js and smart proxy logic)
            DEV_TARGET_API: "https://helpline.sematanzania.org",
            DEV_TARGET_AMI: "https://helpline.sematanzania.org:8384",
            DEV_TARGET_ATI: "https://helpline.sematanzania.org:8384",
            DEV_TARGET_SIP: "https://helpline.sematanzania.org:8089",
            SIP_WS_PATH: "/ws/",
            AMI_WS_PATH: "/ami/sync",
            ATI_WS_PATH: "/ati/sync"
        },
        VOIP: {
            SIP_HOST: "helpline.sematanzania.org",
            SIP_WS_URL: "wss://helpline.sematanzania.org:8089/ws",
            SIP_USER_PREFIX: "0",
            SIP_PASS_PREFIX: "0",
            ICE_SERVERS: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:helpline.sematanzania.org:3479' }
            ]
        },
        ROOTS: {
            CASE_CATEGORY: "362559",
            GENERAL_ASSESSMENT: "362568",
            JUSTICE_SYSTEM_STATE: "362567",
            REFERRAL_TYPE: "362571",
            SERVICE_OFFERED: "362572",
            KNOW_ABOUT_116: "362573",
            AGE_GROUP: "362561",
            GENDER: "362562",
            LOCATION: "362560",
            NATIONALITY: "362564",
            ID_TYPE: "362563",
            LANGUAGE: "362565",
            TRIBE: "362574",
            RELATIONSHIP: "362569",
            DISABILITY: "362570",
            NOT_IN_SCHOOL: "362575",
            SHARES_HOME: "362576",
            OCCUPATION: "362578",
            HEALTH_STATUS: "362577",
            SCHOOL_TYPE: "362583",
            SCHOOL_LEVEL: "362582",
            HIV_STATUS: "362581",
            MARITAL_STATUS: "362580",
            HOUSEHOLD_TYPE: "362579",
            DISPOSITION: "362566",
            GBV_RELATED: "118",
        },
        TRIGGERS: {
            SEXUAL_ABUSE: "362271",
            SERVICE_POLICE: "-999",
            SERVICE_OTHER: "-999",
            REFERRAL_OTHER: "-999",
            SERVICE_REFERAL: "385462",
        },
        DISPOSITIONS: {
            NEW_CASE: "385491",
            FOLLOW_UP: "385491",
            COMPLETE: "385491",
        }
    },

    // --- DEMO / KENYA CLOUD CONFIG ---
    'DEMO': {
        COUNTRY_NAME: "Kenya Cloud",
        COUNTRY_CODE: "254",
        ENDPOINTS: {
            API_BASE: "/api-proxy",
            BACKEND_URL: "https://demo-openchs.bitz-itc.com",
            BACKEND_PATH: "/helpline",
            GATEWAY_AUTH: "https://demo-openchs.bitz-itc.com/api/token/",
            GATEWAY_SEND_MSG: "https://backend.bitz-itc.com/api/whatsapp/send/",
            AMI_HOST: "wss://demo-openchs.bitz-itc.com:8384/ami/sync",
            ATI_HOST: "wss://demo-openchs.bitz-itc.com:8384/ati/sync",
            // Dev Proxy Targets
            DEV_TARGET_API: "https://demo-openchs.bitz-itc.com",
            DEV_TARGET_AMI: "https://demo-openchs.bitz-itc.com:8384",
            DEV_TARGET_ATI: "https://demo-openchs.bitz-itc.com:8384",
            DEV_TARGET_SIP: "https://demo-openchs.bitz-itc.com:8089",
            SIP_WS_PATH: "/ws/",
            AMI_WS_PATH: "/ami/sync",
            ATI_WS_PATH: "/ati/sync"
        },
        VOIP: {
            SIP_HOST: "demo-openchs.bitz-itc.com",
            SIP_WS_URL: "wss://demo-openchs.bitz-itc.com/ws/",
            SIP_USER_PREFIX: "",
            SIP_PASS_PREFIX: "23kdefrtgos09812100",
            ICE_SERVERS: [
                { urls: 'stun:stun.l.google.com:19302' }
            ]
        },
        ROOTS: {
            CASE_CATEGORY: "362557",
            GENERAL_ASSESSMENT: "236694",
            JUSTICE_SYSTEM_STATE: "236687",
            REFERRAL_TYPE: "236707",
            SERVICE_OFFERED: "113",
            KNOW_ABOUT_116: "236700",
            AGE_GROUP: "101",
            GENDER: "120",
            LOCATION: "88",
            NATIONALITY: "126",
            ID_TYPE: "362409",
            LANGUAGE: "123",
            TRIBE: "133",
            RELATIONSHIP: "236634",
            DISABILITY: "236669",
            NOT_IN_SCHOOL: "362466",
            SHARES_HOME: "236631",
            OCCUPATION: "236648",
            HEALTH_STATUS: "236660",
            SCHOOL_TYPE: "236711",
            SCHOOL_LEVEL: "236712",
            HIV_STATUS: "105",
            MARITAL_STATUS: "236654",
            HOUSEHOLD_TYPE: "236674",
            DISPOSITION: "362515",
            GBV_RELATED: "118",
        },
        TRIGGERS: {
            SEXUAL_ABUSE: "362271",
            SERVICE_POLICE: "362036",
            SERVICE_OTHER: "362042",
            REFERRAL_OTHER: "362009",
            SERVICE_REFERAL: "117",
        },
        DISPOSITIONS: {
            NEW_CASE: "363037",
            FOLLOW_UP: "362556",
            COMPLETE: "362527",
        }
    },
};

/**
 * Helper to get the correct config for a country or environment
 */
export function getEnvironmentConfig(countryCode) {
    const code = (countryCode || import.meta.env.VITE_DEFAULT_COUNTRY || 'TZ').toUpperCase();
    return ENVIRONMENT_REGISTRY[code] || ENVIRONMENT_REGISTRY['DEMO'];
}
