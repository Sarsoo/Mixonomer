import React, { Component } from "react";

import { Card, CardContent, Typography, Grid } from '@material-ui/core';

class Index extends Component{

    constructor(props){
        super(props);
        this.state = {}
    }

    render(){
        return (
            <div style={{maxWidth: '500px', margin: 'auto', marginTop: '20px'}}>
            <Card align="center">
                <CardContent>
                    <Grid container>
                        <Grid item xs={12}>
                            <Typography variant="body1">Construct spotify playlists from selections of other playlists</Typography>
                        </Grid>
                        <Grid item xs={12}>
                            <Typography variant="body1">Group sub-genre playlists</Typography>
                        </Grid>
                        <Grid item xs={12}>
                            <Typography variant="body1">Optionally append auto-generated recommendations</Typography>
                        </Grid>
                        <Grid item xs={12}>
                            <Typography variant="body1">Playlists are run multiple times a day</Typography>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>
            </div>
        );
    }
}

export default Index;