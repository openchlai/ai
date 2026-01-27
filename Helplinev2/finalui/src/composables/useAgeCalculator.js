
export function useAgeCalculator() {
    const AGE_GROUP_MAP = {
        '0-5': '361950',
        '6-12': '361951',
        '13-17': '361952',
        '18-24': '361953',
        '25-35': '361954',
        '36-50': '361955',
        '51+': '361956'
    };

    const getAgeGroupFromAge = (age) => {
        if (!age && age !== 0) return '';
        const a = parseInt(age);
        if (isNaN(a) || a < 0) return '';

        if (a < 6) return '0-5';
        if (a <= 12) return '6-12';
        if (a <= 17) return '13-17';
        if (a <= 24) return '18-24';
        if (a <= 35) return '25-35';
        if (a <= 50) return '36-50';
        return '51+';
    };

    const getAgeGroupId = (age) => {
        const text = getAgeGroupFromAge(age);
        return AGE_GROUP_MAP[text] || '';
    };

    const calculateAgeFromDob = (dob) => {
        if (!dob) return '';
        const birthDate = new Date(dob);
        const today = new Date();
        let age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        return age >= 0 ? age.toString() : '';
    };

    const calculateDobFromAge = (age) => {
        if (!age && age !== 0) return '';
        const a = parseInt(age);
        if (isNaN(a) || a < 0) return '';

        const today = new Date();
        const birthYear = today.getFullYear() - a;
        // Default to Jan 1st to encompass the full year possibility usually
        // Construct YYYY-MM-DD
        return `${birthYear}-01-01`;
    };

    return {
        getAgeGroupId,
        calculateAgeFromDob,
        calculateDobFromAge
    };
}
