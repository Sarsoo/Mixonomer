import React from "react";
import { Grid, CircularProgress } from '@material-ui/core';

function Progress (props) {
    return (
        <Grid container justify="flex-start" alignItems="flex-start" align="center" style={{ padding: props.padding }}>
            <Grid item xs={ props.colWidth }>
                <CircularProgress color="secondary" />
            </Grid>
        </Grid>
    );
}

Progress.defaultProps = {
    padding: 36,
    colWidth: 12,
}

export default Progress;