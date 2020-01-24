import React, { Component } from "react";
const axios = require('axios');

import showMessage from "../Toast.js"

class LastFM extends Component {

    constructor(props){
        super(props);
        this.state = {
            lastfm_username: null,
            isLoading: true
        }
        this.getUserInfo();

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    getUserInfo(){
        axios.get('/api/user')
        .then((response) => {

            var username = response.data.lastfm_username;

            if(username == null){
                username = '';
            }

            this.setState({
                lastfm_username: username,
                isLoading: false
            })
        })
        .catch((error) => {
            showMessage(`error getting user info (${error.response.status})`);
        });
    }

    handleChange(event){
        this.setState({
            'lastfm_username': event.target.value
        });
    }

    handleSubmit(event){

        var username = this.state.lastfm_username;

        if(username == ''){
            username = null
        }

        axios.post('/api/user',{
            lastfm_username: username
        }).then((response) => {
            showMessage('saved');
        }).catch((error) => {
            showMessage(`error saving (${error.response.status})`);
        });

        event.preventDefault();

    }

    render(){
        const table =  
            <form onSubmit={this.handleSubmit}>
                <table className="app-table max-width">
                    <thead>
                        <tr>
                            <th colSpan="2"><h1 className="ui-text center-text text-no-select">Last.fm Username</h1></th>
                        </tr>
                    </thead>
                    <tbody>
                    <tr>
                        <td className="ui-text center-text text-no-select">Username:</td>
                        <td><input 
                                type="text" 
                                name="current" 
                                value={this.state.lastfm_username} 
                                onChange={this.handleChange}
                                className="full-width" /></td>
                    </tr>
                    <tr>
                        <td colSpan="2"><input type="submit" style={{width: "100%"}} className="button" value="save" /></td>
                    </tr>
                    </tbody>
                </table>
            </form>;

        const loadingMessage = <p className="center-text text-no-select">Loading...</p>;

        return this.state.isLoading ? loadingMessage : table;
    }
}

export default LastFM;