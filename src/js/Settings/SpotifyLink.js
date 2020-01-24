import React, { Component } from "react";
const axios = require('axios');

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
            <table className="app-table max-width">
                <thead>
                    <tr>
                        <th><h1 className="ui-text center-text text-no-select">Spotify Link</h1></th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td className="ui-text center-text text-no-select">
                            Status: { this.state.spotify_linked ? "Linked" : "Unlinked" }
                        </td>
                    </tr>
                    <tr>
                        <td>
                            { this.state.spotify_linked ? <DeAuthButton /> : <AuthButton /> }
                        </td>
                    </tr>
                </tbody>
            </table>;

        const loadingMessage = <p className="center-text text-no-select">Loading...</p>;

        return this.state.isLoading ? loadingMessage : table;
    }
}

function AuthButton(props) {
    return <a className="button full-width" href="/auth/spotify">Auth</a>;
}

function DeAuthButton(props) {
    return <a className="button full-width" href="/auth/spotify/deauth">De-Auth</a>;
}

export default SpotifyLink;