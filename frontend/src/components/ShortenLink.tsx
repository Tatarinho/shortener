import React, { useState, useEffect } from 'react';
import './ShortenLink.css';
import Logo from '../assets/Logo.svg';
import CopyIcon from '../assets/icon_copy.svg';

interface HistoryItem {
    original: string;
    shortened: string;
}

const ShortenLink: React.FC = () => {
    const [url, setUrl] = useState('');
    const [shortenedUrl, setShortenedUrl] = useState('');
    const [history, setHistory] = useState<HistoryItem[]>(() => {
        const saved = localStorage.getItem('urlHistory');
        return saved ? JSON.parse(saved) : [];
    });

    useEffect(() => {
        localStorage.setItem('urlHistory', JSON.stringify(history));
    }, [history]);

    const updateHistory = (newItem: HistoryItem) => {
        setHistory(prev => {
            const existingIndex = prev.findIndex(
                item => item.original === newItem.original ||
                       item.shortened === newItem.shortened
            );

            if (existingIndex !== -1) {
                const newHistory = [...prev];
                newHistory.splice(existingIndex, 1);
                return [newItem, ...newHistory];
            }

            return [newItem, ...prev].slice(0, 3);
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!url) return;

        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/shorten`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url })
            });

            if (!response.ok) {
                throw new Error('Failed to shorten URL');
            }

            const data = await response.json();
            setShortenedUrl(data.short_url);

            updateHistory({
                original: url,
                shortened: data.short_url
            });

            setUrl('');
        } catch (err) {
            console.error('Error:', err);
        }
    };

    return (
        <div className="app">
            <div className="frame-1">
                <div className="container">
                    <img src={Logo} alt="center.ai logo" className="logo" />
                    <div className="content">
                        <h1 className="title">Short link</h1>
                        <div className="input-filled">
                            <label className="input-label">Link to shortcut</label>
                            <form onSubmit={handleSubmit} className="input-form">
                                <input
                                    type="text"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                    className="url-input"
                                />
                            </form>
                        </div>
                        <button onClick={handleSubmit} className="button-primary">
                            <span className="button-text">Shorten it</span>
                        </button>
                        {shortenedUrl && (
                            <div className="result">
                                <span className="result-text">{shortenedUrl}</span>
                                <button
                                    onClick={() => navigator.clipboard.writeText(shortenedUrl)}
                                    className="icon-copy"
                                >
                                    <img src={CopyIcon} alt="Copy" className="copy-icon" />
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {history.length > 0 && (
                    <div className="frame-5">
                        <div className="frame-4">
                            <span className="last-links">Last links</span>
                        </div>
                        <div className="frame-3">
                            <div className="frame-6">
                                {history.map((item, index) => (
                                    <div
                                        key={index}
                                        className={`result-history ${
                                            index === 0 
                                                ? 'first-item' 
                                                : index === history.length - 1 
                                                    ? 'last-item' 
                                                    : 'middle-item'
                                        }`}
                                    >
                                        <div className="frame-2">
                                            <span className="result-text-original">{item.original}</span>
                                            <span className="result-text-shortened">{item.shortened}</span>
                                        </div>
                                        <button
                                            onClick={() => navigator.clipboard.writeText(item.shortened)}
                                            className="icon-copy"
                                        >
                                            <img src={CopyIcon} alt="Copy" className="copy-icon" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ShortenLink;