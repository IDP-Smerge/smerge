import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import Layout from './Layout.tsx'
import MergeConfictView from './MergeConfictView.tsx'
import { PartialTheme, ThemeProvider } from '@fluentui/react'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import { ToastContainer } from 'react-toastify'

const lightTheme: PartialTheme = {
  semanticColors: {
    bodyBackground: 'white',
    bodyText: 'black',
  },
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
      <div style={{ width: "100vw", position: "absolute", left: "0", top: "0" }}><Layout /></div>
      <ThemeProvider theme={lightTheme}>
        <div style={{ position: "absolute", top: "64px", bottom: "0px", width: "100vw", overflow: "scroll" }}>
          <Router>
            <Routes>
              <Route path="*" element={<MergeConfictView />}></Route>
            </Routes>
          </Router>
        </div>
      </ThemeProvider>
      <ToastContainer theme="dark" />    
  </React.StrictMode>,
)
