import React, { Component } from "react";
const axios = require('axios');

import { Card, Button, CardContent, CardActions, Typography } from "@mui/material";

import showMessage from "../Toast.js"

/**
 * Spotify account link settings card
 */
class SpotifyLink extends Component {

    constructor(props){
        super(props);
        this.state = {
            spotify_linked: null,
            isLoading: true
        }
        this.getUserInfo();
    }

    /**
     * Get user info from API and set spotify link status to state
     */
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

                    {/* STATUS */}
                    <CardContent>
                        <Typography variant="h4" color="textPrimary">Spotify Link</Typography>
                        <Typography variant="body2" color="textSecondary">Status: { this.state.spotify_linked ? "Linked" : "Unlinked" }</Typography>
                    </CardContent>

                    {/* STATE CHANGE BUTTON */}
                    <CardActions>
                        { this.state.spotify_linked ? <DeAuthButton /> : <AuthButton /> }
                    </CardActions>
                </Card>
            </div>;

        const loadingMessage = <p className="center-text text-no-select">Loading...</p>;

        return this.state.isLoading ? loadingMessage : table;
    }
}

/**
 * Authenticate Spotify account button component
 * @param {*} props Properties
 * @returns Button component
 */
function AuthButton(props) {
    return <Button color="secondary" component='a' variant="contained" className="full-width" href="/auth/spotify">Auth</Button>;
}

/**
 * Deauthenticate Spotify account button component
 * @param {*} props Properties
 * @returns Button component
 */
function DeAuthButton(props) {
    return <Button color="secondary" component='a' variant="contained" className="full-width" href="/auth/spotify/deauth">De-Auth</Button>;
}

export default SpotifyLink;