import React, { Component } from "react";
import { BrowserRouter as Redirect } from "react-router-dom";
const axios = require('axios');

import showMessage from "../Toast.js"

class NewPlaylist extends Component {

    constructor(props) {
        super(props);
        this.state = {
            name: '',
            type: 'normal'
        }
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleInputChange(event){
        this.setState({
            [event.target.name]: event.target.value
        });
    }

    handleSubmit(event){
        axios.get('/api/playlists')
        .then((response) => {

            var names = response.data.playlists.map(entry => entry.name)

            var sameName = names.includes(this.state.name);
            if(sameName == false){
                axios.put('/api/playlist', {
                    name: this.state.name,
                    parts: [],
                    playlist_references: [],
                    shuffle: false,
                    type: this.state.type,
                }).then((response) => {
                    showMessage(`${this.state.name} created`);
                }).catch((error) => {
                    showMessage(`error creating playlist (${error.response.status})`);
                });
            }else{
                showMessage('named playlist already exists');
            }
        })
        .catch((error) => {
            showMessage(`error getting playlists (${error.response.status})`);
        });
    }

    render(){
        return (
            <table className="app-table">
                <thead>
                    <tr>
                        <th colSpan="2">
                            <h1 className="ui-text center-text">new playlist</h1>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>
                            <select className="full-width" name="type" onChange={this.handleInputChange}>
                                <option value="default">normal</option>
                                <option value="recents">recents</option>
                            </select>
                        </td>
                        <td>
                            <input 
                                className="full-width" 
                                name="name" 
                                type="text" 
                                value={this.state.name} 
                                onChange={this.handleInputChange}
                                placeholder="name"/>
                        </td>
                    </tr>
                    <tr>
                        <td colSpan="2">
                            <input type="submit" className="button full-width" onClick={this.handleSubmit} value="create" />
                        </td>
                    </tr>
                </tbody>
            </table>
        );
    }

}

export default NewPlaylist;