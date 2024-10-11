import React from "react";
import { createRoot } from 'react-dom/client';
import { ThemeProvider, StyledEngineProvider, makeStyles } from '@mui/styles';
import { createTheme, adaptV4Theme } from '@mui/material/styles';

import MusicTools from "./MusicTools";

const theme = createTheme();

const useStyles = makeStyles((theme) => {
    root: {
        // some CSS that accesses the theme
    }
});

// ROOT file for bootstrapping the Mixonomer component and app

// ReactDOM.render(<MusicTools theme={theme} />, document.getElementById('react'));
const root = createRoot(document.getElementById('react')); // createRoot(container!) if you use TypeScript
root.render(<MusicTools theme={theme} />);