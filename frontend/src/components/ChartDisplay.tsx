'use client';

import { useState } from 'react';
import styles from './ChartDisplay.module.css';

interface WesternData {
    sun: string;
    moon: string;
    mercury: string;
    venus: string;
    mars: string;
    jupiter: string;
    saturn: string;
    ascendant: string;
    dominant_aspects: string[];
}

interface VedicData {
    nakshatra: string;
    nakshatra_pada: number;
    nakshatra_lord: string;
    mahadasha: string;
    mahadasha_ends: string;
    next_dasha: string;
}

interface MahaboteData {
    birth_day: string;
    birth_day_burmese: string;
    house_name: string;
    house_burmese: string;
    ruling_planet: string;
    be_year: number;
    nakshatra_burmese: string;
    grid_number: number;
    characteristics: string;
}

interface ChartDisplayProps {
    western: WesternData;
    vedic: VedicData;
    mahabote: MahaboteData;
}

const MAHABOTE_GRID = [
    { pos: 0, label: 'ဘင်္ဂ', name: 'Binga' },
    { pos: 1, label: 'ရာဇ', name: 'Yaza' },
    { pos: 2, label: 'ဓာတ်', name: 'Athit' },
    { pos: 3, label: 'မဟာ', name: 'Mahat' },
    { pos: 4, label: 'အာတ်', name: 'Atwan' },
    { pos: 5, label: 'သင်္ဃ', name: 'Thinga' },
    { pos: 6, label: 'ရာဟု', name: 'Yat' },
];

export default function ChartDisplay({ western, vedic, mahabote }: ChartDisplayProps) {
    const [activeTab, setActiveTab] = useState<'western' | 'vedic' | 'mahabote'>('western');

    const planets = [
        { name: 'Sun', symbol: '☉', value: western.sun },
        { name: 'Moon', symbol: '☽', value: western.moon },
        { name: 'Mercury', symbol: '☿', value: western.mercury },
        { name: 'Venus', symbol: '♀', value: western.venus },
        { name: 'Mars', symbol: '♂', value: western.mars },
        { name: 'Jupiter', symbol: '♃', value: western.jupiter },
        { name: 'Saturn', symbol: '♄', value: western.saturn },
        { name: 'Ascendant', symbol: 'AC', value: western.ascendant, isAscendant: true },
    ];

    return (
        <div className={styles.container}>
            <div className={styles.tabs}>
                <button
                    className={`${styles.tab} ${activeTab === 'western' ? styles.active : ''}`}
                    onClick={() => setActiveTab('western')}
                >
                    ☉ Western Chart
                </button>
                <button
                    className={`${styles.tab} ${activeTab === 'vedic' ? styles.active : ''}`}
                    onClick={() => setActiveTab('vedic')}
                >
                    🕉 Vedic (Jyotish)
                </button>
                <button
                    className={`${styles.tab} ${activeTab === 'mahabote' ? styles.active : ''}`}
                    onClick={() => setActiveTab('mahabote')}
                >
                    <span className="burmese">မဟာဘုတ်</span>
                </button>
            </div>

            {activeTab === 'western' && (
                <div className={styles.panel}>
                    <h3 className={styles.panelTitle}>Planetary Positions</h3>
                    <div className={styles.planetGrid}>
                        {planets.map((p) => (
                            <div key={p.name} className={`${styles.planetCard} ${p.isAscendant ? styles.ascendant : ''}`}>
                                <span className={styles.planetSymbol}>{p.symbol}</span>
                                <span className={styles.planetName}>{p.name}</span>
                                <span className={styles.planetValue}>{p.value}</span>
                            </div>
                        ))}
                    </div>

                    {western.dominant_aspects.length > 0 && (
                        <div className={styles.aspectList}>
                            <h4>Key Aspects</h4>
                            {western.dominant_aspects.map((a, i) => (
                                <div key={i} className={styles.aspectItem}>
                                    <span className={styles.aspectDot}></span>
                                    {a}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'vedic' && (
                <div className={styles.panel}>
                    <h3 className={styles.panelTitle}>Vedic (Jyotish) Reading</h3>
                    <div className={styles.vedicGrid}>
                        <div className={styles.vedicCard}>
                            <span className={styles.vedicLabel}>Birth Star (Nakshatra)</span>
                            <span className={styles.vedicValue}>{vedic.nakshatra} (Pada {vedic.nakshatra_pada})</span>
                            <span className={styles.vedicSub}>Ruled by {vedic.nakshatra_lord}</span>
                        </div>
                        <div className={styles.vedicCard}>
                            <span className={styles.vedicLabel}>Current Mahadasha</span>
                            <span className={styles.vedicValue}>{vedic.mahadasha}</span>
                            <span className={styles.vedicSub}>Ends: {vedic.mahadasha_ends}</span>
                        </div>
                        <div className={styles.vedicCard}>
                            <span className={styles.vedicLabel}>Next Dasha</span>
                            <span className={styles.vedicValue}>{vedic.next_dasha} Dasha</span>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'mahabote' && (
                <div className={styles.panel}>
                    <h3 className={styles.panelTitle}>
                        <span className="burmese">မဟာဘုတ် (Mahabote Grid)</span>
                    </h3>

                    <div className={styles.mahaboteInfo}>
                        <div className={styles.infoRow}>
                            <span className={`${styles.infoLabel} burmese`}>မွေးနေ့</span>
                            <span className={`${styles.infoValue} burmese`}>{mahabote.birth_day_burmese}</span>
                            <span className={styles.infoEnglish}>({mahabote.birth_day})</span>
                        </div>
                        <div className={styles.infoRow}>
                            <span className={`${styles.infoLabel} burmese`}>ဘုတ်</span>
                            <span className={`${styles.infoValue} burmese`}>{mahabote.house_burmese}</span>
                            <span className={styles.infoEnglish}>({mahabote.house_name})</span>
                        </div>
                        <div className={styles.infoRow}>
                            <span className={styles.infoLabel}>Ruling Planet</span>
                            <span className={styles.infoValue}>{mahabote.ruling_planet}</span>
                        </div>
                        <div className={styles.infoRow}>
                            <span className={styles.infoLabel}>Burmese Era Year</span>
                            <span className={styles.infoValue}>{mahabote.be_year} BE</span>
                        </div>
                    </div>

                    <div className={styles.mahaboteGrid}>
                        {MAHABOTE_GRID.map((cell) => (
                            <div
                                key={cell.pos}
                                className={`${styles.gridCell} ${mahabote.grid_number === cell.pos + 1 ? styles.activeCell : ''}`}
                            >
                                <span className="burmese">{cell.label}</span>
                                <span className={styles.cellName}>{cell.name}</span>
                            </div>
                        ))}
                    </div>

                    <p className={styles.characteristics}>{mahabote.characteristics}</p>
                </div>
            )}
        </div>
    );
}
