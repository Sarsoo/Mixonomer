import { createMuiTheme, responsiveFontSizes } from '@material-ui/core/styles';

let GlobalTheme = createMuiTheme({
    root: {
        flexGrow: 1,
        },
    typography: {
        button: {
        fontSize: '1rem',
        },
    },
    card: {
        display: 'flex',
        spacing: 5
    },
    palette: {
        type: 'dark',
        primary: {
            main: '#1a237e',
        },
        secondary: {
            main: '#1a237e',
        }
    },
    status: {
        danger: 'orange',
    },
});
GlobalTheme = responsiveFontSizes(GlobalTheme);

export default GlobalTheme;