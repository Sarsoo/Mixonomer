import { createMuiTheme, responsiveFontSizes } from '@material-ui/core/styles';

let GlobalTheme = createMuiTheme({
    root: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
    },
    spacing: 4,
    typography: {
        button: {
        fontSize: '1rem',
        },
    },
    paper: {
        display: 'flex',
        spacing: 5
    },
    card: {
        marginTop: 24,
        display: 'flex',
        spacing: 5
    },
    palette: {
        type: 'dark',
        primary: {
            main: '#1976d2',
        },
        secondary: {
            main: '#dc004e',
        },
        error: {
            main: '#f44336'
        }
    },
    status: {
        danger: 'orange',
    }
});
GlobalTheme = responsiveFontSizes(GlobalTheme);

export default GlobalTheme;