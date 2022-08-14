import { createTheme, responsiveFontSizes } from '@material-ui/core/styles';

let GlobalTheme = createTheme({
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
        // https://colorhunt.co/palette/907fa4a58faaa6d6d6ededd0
        primary: {
            main: '#907FA4',
        },
        secondary: {
            main: '#A6D6D6',
        },
        // https://colorhunt.co/palette/de89717b6079a7d0cdffe9d6
        error: {
            main: '#DE8971'
        },
        info: {
            main: "#A7D0CD"
        },
    },
    status: {
        danger: 'orange',
    }
});
GlobalTheme = responsiveFontSizes(GlobalTheme);

export default GlobalTheme;