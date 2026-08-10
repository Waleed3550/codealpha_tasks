import { Navbar } from './Navbar';

export const Layout = ({ children }) => {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: 'var(--bg-color)', color: 'var(--text-color)', transition: 'background-color 0.3s ease, color 0.3s ease' }}>
            <Navbar />
            <div style={{ flex: 1, marginTop: '60px', width: '100%', display: 'flex', justifyContent: 'center', padding: '30px 20px' }}>
                <div style={{ width: '100%', maxWidth: '1128px' }}>
                    {children}
                </div>
            </div>
        </div>
    );
};


