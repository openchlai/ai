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
    // Sometimes rawMsg is just the text, sometimes base64. 
    // The previous implementation blindly tried to decode.
    // Let's stick to the previous robust decode that catches errors.
    try {
        decodedText = decodeContent(rawMsg)
    } catch (e) {
        decodedText = rawMsg
    }

    return {
        id: get('id') || get('_uid') || get('uid'),
        threadId: get('src_callid') || get('src_address'), // Fallback to address if callid missing
        address: get('src_address'),
        platform: get('src'),
        direction: get('src_vector'), // 1=Inbound, 2=Outbound typically
        sender: get('created_by') || get('src_address'),
        text: decodedText,
        timestamp: get('dth') || get('created_at') || get('created_on'), // Add created_at/created_on fallback
        status: get('src_status'),
        isClosed: (decodedText && (decodedText.includes('*closed*') || decodedText.trim() === 'close')) || false,
        raw: row // Keep raw reference
    }
}

export const normalizeMessages = (rows, schema) => {
    if (!Array.isArray(rows) || !schema) return []
    return rows.map(row => normalizeMessage(row, schema)).filter(Boolean)
}
