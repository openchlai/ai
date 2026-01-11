import { ref } from 'vue'
import axios from 'axios'

export function useAgentPresence() {
    const agentPresenceChannels = ref([])
    const loading = ref(false)
    const error = ref(null)

    // Create a dedicated instance for the agent status server
    const agentAxios = axios.create({
        baseURL: __APP_AGENT_STATUS_URL__,
        timeout: 5000
    })

    const parseAmiData = (data) => {
        let chArr = []
        // Use either obj.channels or the root object itself
        const sourceChannels = data.channels || data

        if (Array.isArray(sourceChannels)) {
            chArr = sourceChannels
        } else if (sourceChannels && typeof sourceChannels === 'object') {
            chArr = Object.entries(sourceChannels).map(([key, arr]) => {
                if (Array.isArray(arr)) {
                    return {
                        _uid: key,
                        CHAN_TS: arr[1] || Date.now(),
                        CHAN_UNIQUEID: arr[2] || key,
                        CHAN_CHAN: arr[3] || '',
                        CHAN_CALLERID_NUM: arr[4] || '',
                        CHAN_CALLERID_NAME: arr[5] || '',
                        CHAN_CONTEXT: arr[6] || '',
                        CHAN_EXTEN: arr[7] || '',
                        CHAN_ACTION_ID: arr[8] || '',
                        CHAN_STATE_UP: arr[13] || 0,
                        CHAN_STATE_QUEUE: arr[14] || 0,
                        CHAN_STATE_CONNECT: arr[15] || 0,
                        CHAN_STATE_HANGUP: arr[16] || 0,
                        CHAN_STATE_HOLD: arr[18] || 0,
                        CHAN_CBO_TS: arr[20] || '',
                        CHAN_CBO: arr[21] || '',
                        CHAN_CBO_UNIQUEID: arr[22] || '',
                        CHAN_CBO_CID: arr[23] || '',
                        CHAN_XFER_TS: arr[24] || '',
                        CHAN_XFER: arr[25] || '',
                        CHAN_XFER_UNIQUEID: arr[26] || '',
                        CHAN_XFER_CID: arr[27] || '',
                        CHAN_ORIG: arr[36] || '',
                        CHAN_CONTEXT_MASQ: arr[43] || '',
                        CHAN_EXTEN_MASQ: arr[44] || '',
                        CHAN_UNIQUEID_2: arr[45] || '',
                        CHAN_CHAN_2: arr[46] || '',
                        CHAN_CID_NUM_2: arr[47] || '',
                        CHAN_SIPCALLID: arr[50] || '',
                        CHAN_BRIDGE_ID: arr[51] || '',
                        CHAN_CAMPAIGN_ID: arr[53] || '',
                        CHAN_CAMPAIGN_WRAPUP: arr[54] || '',
                        CHAN_PROMPT_TS0: arr[67] || '',
                        CHAN_VECTOR: arr[74] || '',
                        CHAN_EVENT: arr[76] || '',
                        CHAN_EVENT_N: arr[77] || '',
                        CHAN_SIPID_JS_: arr[80] || '',
                        CHAN_STATUS_: arr[81] || '',
                        CHAN_STATUS_TXT_: arr[82] || '',
                        CHAN_STATUS_TS_: arr[83] || '',
                        CHAN_STATUS_TS_TXT_: arr[84] || '',
                        _raw: arr
                    }
                }
                return { _uid: key, ...arr }
            })
        }
        return chArr
    }

    const fetchAgentPresence = async () => {
        loading.value = true
        error.value = null

        try {
            const response = await agentAxios.get('/sync', {
                params: {
                    c: '7711987',
                    d: '',
                    n: '1'
                }
            })

            console.log('Agent Presence API Response:', response.data)

            if (response.data) {
                agentPresenceChannels.value = parseAmiData(response.data)
            }
        } catch (err) {
            console.error('Error fetching agent presence:', err)
            error.value = err.message
        } finally {
            loading.value = false
        }
    }

    return {
        agentPresenceChannels,
        loading,
        error,
        fetchAgentPresence
    }
}
