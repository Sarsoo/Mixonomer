import React, { Component } from "react";
const axios = require('axios');

import { Card, Button, CardContent, CardActions, Typography } from "@material-ui/core";

import showMessage from "../Toast.js"

class SpotifyLink extends Component {

    constructor(props){
        super(props);
        this.state = {
            spotify_linked: null,
            isLoading: true
        }
        this.getUserInfo();
    }

    getUserInfo(){
        axios.get('/api/user')
        .then((response) => {
            this.setState({
                spotify_linked: response.data.spotify_linked,
                isLoading: false
            })
        })
        .catch((error) => {
            showMessage(`error getting user info (${error.response.status})`);
        });
    }

    render(){
        const table =  
            <div style={{maxWidth: '400px', margin: 'auto', marginTop: '20px'}}>
                <Card align="center">
                    <CardContent>
                        <Typography variant="h4" color="textPrimary">Admin Functions</Typography>
                        <Typography variant="body2" color="textSecondary">Status: { this.state.spotify_linked ? "Linked" : "Unlinked" }</Typography>
                    </CardContent>
                    <CardActions>
                        { this.state.spotify_linked ? <DeAuthButton /> : <AuthButton /> }
                    </CardActions>
                </Card>
            </div>;

        const loadingMessage = <p className="center-text text-no-select">Loading...</p>;

        return this.state.isLoading ? loadingMessage : table;
    }
}

function AuthButton(props) {
    return <Button component='a' variant="contained" className="full-width" href="/auth/spotify">Auth</Button>;
}

function DeAuthButton(props) {
    return <Button component='a' variant="contained" className="full-width" href="/auth/spotify/deauth">De-Auth</Button>;
}

export default SpotifyLink;