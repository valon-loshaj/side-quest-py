import reactLogo from './assets/react.svg';
import viteLogo from '/vite.svg';
import './App.css';
import Layout from './layout/Layout';
function App() {
    return (
        <Layout>
            <h1>Side Quest Application</h1>
            <p>
                Welcome to the Side Quest Application built with React and TypeScript.
            </p>
            <div>
                <a href="https://vite.dev" target="_blank">
                    <img src={viteLogo} className="logo" alt="Vite logo" />
                </a>
                <a href="https://react.dev" target="_blank">
                    <img src={reactLogo} className="logo react" alt="React logo" />
                </a>
            </div>
        </Layout>
    );
}

export default App;
