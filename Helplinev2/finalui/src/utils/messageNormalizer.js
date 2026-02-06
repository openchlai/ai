export const normalizeMessage = (row, schema) => {
    if (!row) return null

    // Determine strategy: Array (Schema) or Object (Direct)
    const isArray = Array.isArray(row)
    if (isArray && !schema) return null // Schema required for array

    // Helper to safely get value by key
    const get = (key) => {
        if (isArray) {
            const idx = schema[key]?.[0]
            return idx !== undefined ? row[idx] : undefined
        } else {
            return row[key]
        }
    }

    // Base64 Decode Helper
    const decodeContent = (raw) => {
        if (!raw) return ''
        try {
            // Check if it's likely base64 (simple heuristic or just try)
            // Some APIs return already decoded text? Or double encoded?
            // If it has spaces, likely not base64 (unless it's a sentence).
            // A safer Base64 check:
            const isBase64 = /^[A-Za-z0-9+/=]+$/.test(raw) && raw.length % 4 === 0
            if (isBase64) {
                return decodeURIComponent(escape(atob(raw)))
            }
            return raw
        } catch (e) {
            return raw // Return original if decode fails
        }
    }

    const rawMsg = get('src_msg')
    let decodedText = ''
    let aiMetadata = null

    try {
        decodedText = decodeContent(rawMsg)

        // Try to identify if this is an AI payload
        if (decodedText && (decodedText.trim().startsWith('{') || decodedText.trim().startsWith('['))) {
            try {
                const parsed = JSON.parse(decodedText)
                if (parsed.call_metadata) {
                    aiMetadata = parsed.call_metadata
                }
            } catch (je) { }
        }
    } catch (e) {
        decodedText = rawMsg
    }

    const srcAddress = get('src_address')
    const srcCallId = get('src_callid')
    const platform = get('src')

    // Improved address: Use callerid from AI metadata if available, then fallback to srcAddress
    const address = String(aiMetadata?.callerid || aiMetadata?.phone || srcAddress || 'Unknown').trim()

    // Improved threadId: Use call_id from AI metadata if top-level src_callid is missing
    const threadId = String(srcCallId || aiMetadata?.call_id || address).trim()

    return {
        id: get('id') || get('_uid') || get('uid'),
        threadId: threadId,
        address: address,
        platform: platform,
        direction: get('src_vector'), // 1=Inbound, 2=Outbound typically
        sender: get('created_by') || address,
        text: decodedText,
        timestamp: get('dth') || get('created_at') || get('created_on'),
        status: get('src_status'),
        isClosed: (decodedText && (decodedText.includes('*closed*') || decodedText.trim() === 'close')) || false,
        raw: row // Keep raw reference
    }
}

export const normalizeMessages = (rows, schema) => {
    if (!Array.isArray(rows) || !schema) return []
    return rows.map(row => normalizeMessage(row, schema)).filter(Boolean)
}
