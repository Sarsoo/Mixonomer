import React, { Component } from "react";
const axios = require('axios');

import showMessage from "../Toast.js";
import BarChart from "./BarChart.js";
import PieChart from "./PieChart.js";

class Stats extends Component {

    constructor(props){
        super(props);
        this.state = {
            playlists: [],
            isLoading: true,
            isLoadingPlaylist: false,
            subjectPlaylistName: '',
            currentPlaylist: null
        }
        this.getPlaylists();

        this.handleInputChange = this.handleInputChange.bind(this);
    }

    getPlaylists(){
        axios.get('/api/spotify/playlist')
        .then((response) => {

            var playlists = response.data.playlists;

            playlists.sort(function(a, b){
                if(a.toLowerCase() < b.toLowerCase()) { return -1; }
                if(a.toLowerCase() > b.toLowerCase()) { return 1; }
                return 0;
            });

            this.setState({
                playlists: playlists,
                isLoading: false
            });
        })
        .catch((error) => {
            console.log(error);
            showMessage(`error getting playlists (${error.response.status})`);
        });
    }

    getPlaylist(){
        axios.get(`/api/spotify/playlist/stats?name=\'${this.state.subjectPlaylistName}\'`)
        .then((response) => {
            this.setState({
                currentPlaylist: response.data.playlist,
                isLoadingPlaylist: false
            });
        })
        .catch((error) => {
            console.log(error);
            showMessage(`error getting ${this.state.subjectPlaylistName} (${error.response.status})`);
        });
    }

    handleInputChange(event){
        this.setState({
            [event.target.name]: event.target.value
        });

        if (event.target.name == "subjectPlaylistName"){
            this.setState({
                isLoadingPlaylist: true
            })
            this.getPlaylist();
        }
    }

    render() {

        var table = <div>
            <table className="app-table max-width">
                <thead>
                    <tr>
                        <th colSpan='3'>
                            <h1 className="ui-text center-text text-no-select">playlist stats</h1>
                        </th>
                    </tr>
                    <tr>
                        <th><select name="subjectPlaylistName" 
                                className="full-width"
                                value={this.state.subjectPlaylistName}
                                onChange={this.handleInputChange}>
                            { this.state.playlists.map((entry) => <PlaylistNameEntry name={entry} key={entry} />) }
                        </select></th>
                    </tr>
                </thead>
                { this.state.isLoadingPlaylist == false && this.state.currentPlaylist != null &&
                    <PlaylistView playlist={this.state.currentPlaylist}/>
                }
            </table>
            </div>;

        const loadingMessage = <p className="center-text">loading...</p>;

        return this.state.isLoading ? loadingMessage : table;
    }
}

class PlaylistView extends Component {

    constructor(props){
        super(props);
        this.state = {
            currentPlaylist: props.currentPlaylist
        }
    }

    render() {
        return <tbody>
            <tr>
                <td>{this.state.currentPlaylist.name}</td>
            </tr>
        </tbody>;
    }

}

function PlaylistNameEntry(props) {
    return <option value={props.name}>{props.name}</option>;
}

export default Stats;