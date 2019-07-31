import React, { Component } from "react";
const axios = require('axios');

class SpotifyLink extends Component {

    constructor(props){
        super(props);
        this.state = {
            spotify_linked: props.spotify_linked
        }
    }

    getUserInfo(){

    }

    render(){
        return (
            <table className="app-table max-width">
                <thead>
                    <tr>
                        <th><h1 className="ui-text center-text">spotify link status</h1></th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td className="ui-text center-text">
                            status: { this.state.spotify_linked ? "linked" : "unlinked" }
                        </td>
                    </tr>
                    <tr>
                        <td>
                            { this.state.spotify_linked ? <DeAuthButton /> : <AuthButton /> }
                        </td>
                    </tr>
                </tbody>
            </table>
        );
    }
}

function AuthButton(props) {
    return <a className="button full-width" href="/auth/spotify">auth</a>;
}

function DeAuthButton(props) {
    return <a className="button full-width" href="/auth/spotify/deauth">de-auth</a>;
}

export default SpotifyLink;