'use client';

import styles from './ReadingResult.module.css';

interface ReadingResultProps {
    reading: string;
}

const SECTION_PATTERNS = [
    { key: 'introduction', burmese: 'နိဒါန်း', english: 'Introduction' },
    { key: 'past', burmese: 'အတိတ်', english: 'Past (အတိတ်)' },
    { key: 'present', burmese: 'ပစ္စုပ္ပန်', english: 'Present (ပစ္စုပ္ပန်)' },
    { key: 'future', burmese: 'အနာဂတ်', english: 'Future (အနာဂတ်)' },
    { key: 'remedy', burmese: 'ယတြာ', english: 'Remedy (ယတြာ)' },
];

const SECTION_ICONS: Record<string, string> = {
    introduction: '✨',
    past: '🌑',
    present: '🌕',
    future: '⭐',
    remedy: '🌿',
};

function parseReadingIntoSections(reading: string): Array<{ title: string; icon: string; content: string }> {
    const sections: Array<{ title: string; icon: string; content: string }> = [];

    // Try to split by markdown-style bold headers like **နိဒါန်း (Introduction):**
    const headerRegex = /\*\*(.*?)\*\*/g;
    const parts = reading.split(/(?=\*\*)/);

    if (parts.length > 1) {
        for (const part of parts) {
            const match = part.match(/^\*\*(.*?)\*\*[:\s]*([\s\S]*)/);
            if (match) {
                const title = match[1].trim();
                const content = match[2].trim();
                const keyMatch = SECTION_PATTERNS.find(s =>
                    title.includes(s.burmese) || title.includes(s.english.split(' ')[0])
                );
                sections.push({
                    title,
                    icon: keyMatch ? SECTION_ICONS[keyMatch.key] : '◆',
                    content,
                });
            }
        }
    }

    // If no structured sections found, return the whole text as one block
    if (sections.length === 0) {
        sections.push({ title: 'Generated Reading', icon: '✨', content: reading });
    }

    return sections;
}

export default function ReadingResult({ reading }: ReadingResultProps) {
    const sections = parseReadingIntoSections(reading);

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <span className={styles.headerIcon}>🔮</span>
                <div>
                    <h2 className={`${styles.title} burmese`}>ဟောစာတမ်း</h2>
                    <p className={styles.subtitle}>AI-Generated Astrological Reading</p>
                </div>
            </div>

            <div className={styles.sections}>
                {sections.map((section, i) => (
                    <div key={i} className={styles.section} style={{ animationDelay: `${i * 0.1}s` }}>
                        <div className={styles.sectionHeader}>
                            <span className={styles.sectionIcon}>{section.icon}</span>
                            <h3 className={`${styles.sectionTitle} burmese`}>{section.title}</h3>
                        </div>
                        <div className={`${styles.sectionContent} burmese`}>
                            {section.content}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
