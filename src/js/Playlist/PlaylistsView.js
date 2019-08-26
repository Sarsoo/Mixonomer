import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link } from "react-router-dom";
const axios = require('axios');

import showMessage from "../Toast.js"

class PlaylistsView extends Component {

    constructor(props){
        super(props);
        this.state = {
            isLoading: true
        }
        this.getPlaylists();
        this.handleRunPlaylist = this.handleRunPlaylist.bind(this);
        this.handleDeletePlaylist = this.handleDeletePlaylist.bind(this);
        this.handleRunAll = this.handleRunAll.bind(this);
    }

    getPlaylists(){
        var self = this;
        axios.get('/api/playlists')
        .then((response) => {

            var playlists = response.data.playlists.slice();
            
            playlists.sort(function(a, b){
                if(a.name.toLowerCase() < b.name.toLowerCase()) { return -1; }
                if(a.name.toLowerCase() > b.name.toLowerCase()) { return 1; }
                return 0;
            });

            self.setState({
                playlists: playlists,
                isLoading: false
            });
        })
        .catch((error) => {
            showMessage(`error getting playlists (${error.response.status})`);
        });
    }

    handleRunPlaylist(name, event){
        axios.get('/api/user')
        .then((response) => {
            if(response.data.spotify_linked == true){
                axios.get('/api/playlist/run', {params: {name: name}})
                .then((response) => {
                    showMessage(`${name} ran`);
                })
                .catch((error) => {
                    showMessage(`error running ${name} (${error.response.status})`);
                });
            }else{
                showMessage(`link spotify before running`);
            }
        }).catch((error) => {
            showMessage(`error running ${this.state.name} (${error.response.status})`);
        });
    }

    handleDeletePlaylist(name, event){
        axios.delete('/api/playlist', { params: { name: name } })
        .then((response) => {
            showMessage(`${name} deleted`);
            this.getPlaylists();
        }).catch((error) => {
            showMessage(`error deleting ${name} (${error.response.status})`);
        });
    }

    handleRunAll(event){
        axios.get('/api/user')
        .then((response) => {
            if(response.data.spotify_linked == true){
                axios.get('/api/playlist/run/user')
                .then((response) => {
                    showMessage("all playlists ran");
                })
                .catch((error)  => {
                    showMessage(`error running all (${error.response.status})`);
                });
            }else{
                showMessage(`link spotify before running`);
            }
        }).catch((error) => {
            showMessage(`error running ${this.state.name} (${error.response.status})`);
        });
    }

    render() {
        
        const table =   <Table playlists={this.state.playlists} 
                            handleRunPlaylist={this.handleRunPlaylist} 
                            handleDeletePlaylist={this.handleDeletePlaylist}
                            handleRunAll={this.handleRunAll}/>;

        const loadingMessage = <p className="center-text">loading...</p>;

        return this.state.isLoading ? loadingMessage : table;
    }
}

function Table(props){
    return (
        <table className="app-table max-width">
            { props.playlists.length == 0 ? (
                <tbody>
                    <tr>
                        <td className="ui-text text-no-select center-text">
                            no playlists
                        </td>
                    </tr>
                </tbody>
            ) : (
            <tbody>
                { props.playlists.map((playlist) => <Row playlist={ playlist } 
                                                        handleRunPlaylist={props.handleRunPlaylist} 
                                                        handleDeletePlaylist={props.handleDeletePlaylist}
                                                        key={ playlist.name }/>) }
                <tr>
                    <td colSpan="3"><button className="full-width button" onClick={props.handleRunAll}>run all</button></td>
                </tr>
            </tbody>
            )}
        </table>
    );
}

function Row(props){
    return (
        <tr>
            <PlaylistLink playlist={props.playlist}/>
            <td style={{width: "100px"}}><button className="button" style={{width: "100px"}} onClick={(e) => props.handleRunPlaylist(props.playlist.name, e)}>run</button></td>
            <td style={{width: "100px"}}><button className="button"  style={{width: "100px"}} onClick={(e) => props.handleDeletePlaylist(props.playlist.name, e)}>delete</button></td>
        </tr>
    );
}

function PlaylistLink(props){
    return (
        <td>
            <Link to={ getPlaylistLink(props.playlist.name) } className="button full-width">{ props.playlist.name }</Link>
        </td>
    );
}

function getPlaylistLink(playlistName){
    return '/app/playlist/' + playlistName;
}

export default PlaylistsView;