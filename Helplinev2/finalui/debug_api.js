import axios from 'axios'
async function check() {
    try {
        const res = await axios.get('https://helpline.sematanzania.org/hh19jan2026/api/activities/', {
            params: { _c: 5 },
            headers: { 'Session-Id': 'test' } // Might not work without real session
        })
        console.log(JSON.stringify(res.data, null, 2))
    } catch (e) {
        console.log('Error:', e.message)
    }
}
check()
