import React, { useState } from 'react';
import { Users, Lock, Cloud, X, Plus } from 'lucide-react';
import styles from './UserIntegrations.module.css';

export default function UserIntegrations({ user }) {
    const [groups, setGroups] = useState([]);
    const [oidcAccounts, setOidcAccounts] = useState([]);
    const [samlAccounts, setSamlAccounts] = useState([]);

    const handleRemoveGroup = (groupId) => {
        setGroups((prev) => prev.filter((g) => g.id !== groupId));
    };

    const handleRemoveOidc = (accountId) => {
        setOidcAccounts((prev) => prev.filter((acc) => acc.id !== accountId));
    };

    return (
        <div className={styles.container}>
            {/* --- SECTION 1: GROUPS --- */}
            <div className={styles.card}>
                <div className={styles.cardHeader}>
                    <h3 className={styles.cardTitle}>Groups</h3>
                    <Users size={20} className={styles.cardIcon} />
                </div>
                <div className={styles.cardBody}>
                    <table className={styles.table}>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th style={{ width: '120px', textAlign: 'right' }}></th>
                            </tr>
                        </thead>
                        <tbody>
                            {groups.length > 0 ? (
                                groups.map((group) => (
                                    <tr key={group.id}>
                                        <td className={styles.itemLink}>{group.name}</td>
                                        <td style={{ textAlign: 'right' }}>
                                            <button 
                                                type="button" 
                                                className={styles.removeBtn}
                                                onClick={() => handleRemoveGroup(group.id)}
                                            >
                                                <X size={14} strokeWidth={2.5} /> Remove
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="2" className={styles.emptyText}>No groups assigned.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                    <button type="button" className={styles.addBtn}>
                        <Plus size={16} strokeWidth={2.5} /> Add to group
                    </button>
                </div>
            </div>

            {/* --- SECTION 2: OPENID-CONNECT ACCOUNTS --- */}
            <div className={styles.card}>
                <div className={styles.cardHeader}>
                    <h3 className={styles.cardTitle}>OpenID-Connect accounts</h3>
                    <Lock size={20} className={styles.cardIcon} />
                </div>
                <div className={styles.cardBody}>
                    <table className={styles.table}>
                        <thead>
                            <tr>
                                <th>Issuer</th>
                                <th>Subject</th>
                                <th style={{ width: '120px', textAlign: 'right' }}></th>
                            </tr>
                        </thead>
                        <tbody>
                            {oidcAccounts.length > 0 ? (
                                oidcAccounts.map((account) => (
                                    <tr key={account.id}>
                                        <td className={styles.monoText}>{account.issuer}</td>
                                        <td className={styles.monoText}>{account.subject}</td>
                                        <td style={{ textAlign: 'right' }}>
                                            <button 
                                                type="button" 
                                                className={styles.removeBtn}
                                                onClick={() => handleRemoveOidc(account.id)}
                                            >
                                                <X size={14} strokeWidth={2.5} /> Remove
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="3" className={styles.emptyText}>No OpenID-Connect accounts linked.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                    <button type="button" className={styles.addBtn}>
                        <Plus size={16} strokeWidth={2.5} /> Add OpenID-Connect account
                    </button>
                </div>
            </div>

            {/* --- SECTION 3: SAML ACCOUNTS --- */}
            <div className={styles.card}>
                <div className={styles.cardHeader}>
                    <h3 className={styles.cardTitle}>Saml accounts</h3>
                    <Cloud size={20} className={styles.cardIcon} />
                </div>
                <div className={styles.cardBody}>
                    {samlAccounts.length > 0 ? (
                        <table className={styles.table}>
                            <thead>
                                <tr>
                                    <th>Provider</th>
                                    <th>Identifier</th>
                                    <th style={{ width: '120px', textAlign: 'right' }}></th>
                                </tr>
                            </thead>
                            <tbody>
                                {samlAccounts.map((account) => (
                                    <tr key={account.id}>
                                        <td>{account.provider}</td>
                                        <td>{account.identifier}</td>
                                        <td style={{ textAlign: 'right' }}>
                                            <button type="button" className={styles.removeBtn}>
                                                <X size={14} strokeWidth={2.5} /> Remove
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <div className={styles.emptyState}>
                            <span>No SAML accounts linked.</span>
                        </div>
                    )}
                    <button type="button" className={styles.addBtn}>
                        <Plus size={16} strokeWidth={2.5} /> Add Saml account
                    </button>
                </div>
            </div>
        </div>
    );
}
