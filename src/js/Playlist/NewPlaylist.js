import React, { Component } from "react";
import { BrowserRouter as Redirect } from "react-router-dom";
const axios = require('axios');

import showMessage from "../Toast.js"

class NewPlaylist extends Component {

    constructor(props) {
        super(props);
        this.state = {
            name: '',
            type: 'default',
            description: ''
        }
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    componentDidMount(){
        this.setDescription('default');
    }

    setDescription(value){
        switch(value){
            case 'default':
                this.setState({
                    description: 'merge playlists as-is with deduplication by spotify id'
                })
                break;
            case 'recents':
                this.setState({
                    description: "select songs from playlists which have been added since a variable number of days"
                })
                break;
        }
    }

    handleInputChange(event){
        this.setState({
            [event.target.name]: event.target.value
        });
        this.setDescription(event.target.value);
    }

    handleSubmit(event){
        var name = this.state.name;
        this.setState({
            name: ''
        });

        if(name.length != 0){
            axios.get('/api/playlists')
            .then((response) => {

                var names = response.data.playlists.map(entry => entry.name)

                var sameName = names.includes(this.state.name);
                if(sameName == false){
                    axios.put('/api/playlist', {
                        name: name,
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
        }else{
            showMessage('enter name');
        }
    }

    render(){
        return (
            <table className="app-table max-width">
                <thead>
                    <tr>
                        <th colSpan="2">
                            <h1 className="ui-text center-text text-no-select">new playlist</h1>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>
                            <select className="full-width" name="type" onChange={this.handleInputChange}>
                                <option value="default">default</option>
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
                    <tr>
                        <td colSpan="2" className="ui-text text-no-select center-text">
                            <br></br>{this.state.description}
                        </td>
                    </tr>
                </tbody>
            </table>
        );
    }

}

export default NewPlaylist;