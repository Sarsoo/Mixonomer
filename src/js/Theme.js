import { createMuiTheme, responsiveFontSizes } from '@material-ui/core/styles';

let GlobalTheme = createMuiTheme({
    root: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        spacing: 20
    },
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
        display: 'flex',
        spacing: 5
    },
    palette: {
        type: 'dark',
        primary: {
            main: '#1a237e',
        },
        secondary: {
            main: '#2196f3',
        }
    },
    status: {
        danger: 'orange',
    }
});
GlobalTheme = responsiveFontSizes(GlobalTheme);

export default GlobalTheme;