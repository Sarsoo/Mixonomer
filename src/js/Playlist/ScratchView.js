import React, { Component } from "react";
const axios = require('axios');

import showMessage from "../Toast.js"

class ScratchView extends Component{

    constructor(props){
        super(props);
        this.state = {
            name: 'play',
            parts: [],
            playlists: [],
            filteredPlaylists: [],
            playlist_references: [],
            type: 'default',

            day_boundary: 5,
            recommendation_sample: 5,
            newPlaylistName: '',
            newPlaylistReference: '',

            shuffle: false,
            include_recommendations: false
        }
        this.handleAddPart = this.handleAddPart.bind(this);
        this.handleAddReference = this.handleAddReference.bind(this);
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleRemoveRow = this.handleRemoveRow.bind(this);
        this.handleRemoveRefRow = this.handleRemoveRefRow.bind(this);

        this.handleRun = this.handleRun.bind(this);

        this.handleShuffleChange = this.handleShuffleChange.bind(this);
        this.handleRecChange = this.handleRecChange.bind(this);
    }

    componentDidMount(){

        this.getPlaylists();
    }


    getPlaylists(){
        return axios.get(`/api/playlists`)
        .then((response) => {
            var filteredPlaylists = response.data.playlists.filter((entry) => entry.name != this.state.name);

            this.setState({
                playlists: response.data.playlists,
                newPlaylistReference: filteredPlaylists.length > 0 ? filteredPlaylists[0].name : ''
            });
        })
        .catch((error) => {
            showMessage(`error getting playlists (${error.response.status})`);
        });
    }

    handleInputChange(event){
        this.setState({
            [event.target.name]: event.target.value
        });
    }

    handleTypeChange(sample){
        axios.post('/api/playlist', {
            name: this.state.name,
            type: sample
        }).catch((error) => {
            showMessage(`error updating type (${error.response.status})`);
        });
    }

    handleShuffleChange(event) {
        this.setState({
            shuffle: event.target.checked
        });
    }

    handleRecChange(event) {
        this.setState({
            include_recommendations: event.target.checked
        });
    }

    handleAddPart(event){
        
        if(this.state.newPlaylistName.length != 0){

            var check = this.state.parts.includes(this.state.newPlaylistName);

            if(check == false) {
                var parts = this.state.parts.slice();
                parts.push(this.state.newPlaylistName);

                parts.sort(function(a, b){
                    if(a < b) { return -1; }
                    if(a > b) { return 1; }
                    return 0;
                });

                this.setState({
                    parts: parts,
                    newPlaylistName: ''
                });
            }else{
                showMessage('playlist already added');  
            }

        }else{
            showMessage('enter playlist name');
        }
    }

    handleAddReference(event){

        if(this.state.newPlaylistReference.length != 0){
            
            var check = this.state.playlist_references.includes(this.state.newPlaylistReference);

            if(check == false) {
                var playlist_references = this.state.playlist_references.slice();
                playlist_references.push(this.state.newPlaylistReference);
                
                playlist_references.sort(function(a, b){
                    if(a < b) { return -1; }
                    if(a > b) { return 1; }
                    return 0;
                });

                var filteredPlaylists = this.state.playlists.filter((entry) => entry.name != this.state.name);
                
                this.setState({
                    playlist_references: playlist_references,
                    newPlaylistReference: filteredPlaylists.length > 0 ? filteredPlaylists[0].name : ''
                });

            }else{
                showMessage('playlist already added');  
            }

        }else{
            showMessage('no other playlists to add');   
        }
    }

    handleRemoveRow(id, event){
        var parts = this.state.parts;
        parts = parts.filter(e => e !== id);
        this.setState({
            parts: parts
        });

        if(parts.length == 0) {
            parts = -1;
        }
    }

    handleRemoveRefRow(id, event){
        var playlist_references = this.state.playlist_references;
        playlist_references = playlist_references.filter(e => e !== id);
        this.setState({
            playlist_references: playlist_references
        });
    }

    handleRun(event){
        if(this.state.playlist_references.length > 0 || this.state.parts.length > 0){
            axios.get('/api/user')
            .then((response) => {
                if(response.data.spotify_linked == true){
                    axios.post('/api/playlist/play', {
                        parts: this.state.parts,
                        playlists: this.state.playlist_references,
                        shuffle: this.state.shuffle,
                        include_recommendations: this.state.include_recommendations,
                        recommendation_sample: this.state.recommendation_sample,
                        day_boundary: this.state.day_boundary,
                        playlist_type: this.state.type
                    })
                    .then((reponse) => {
                        showMessage(`played`);
                    })
                    .catch((error) => {
                        showMessage(`error playing (${error.response.status})`);
                    });
                }else{
                    showMessage(`link spotify before running`);
                }
            }).catch((error) => {
                showMessage(`error playing (${error.response.status})`);
            });
        }else{
            showMessage(`add either playlists or parts`);
        }
    }

    render(){

        const table = (
            <table className="app-table max-width">
                {/* <thead>
                    <tr>
                        <th colSpan="2"><h1 className="text-no-select">{ this.state.name }</h1></th>
                    </tr>
                </thead> */}
                { this.state.playlist_references.length > 0 && <ListBlock name="managed" handler={this.handleRemoveRefRow} list={this.state.playlist_references}/> }
                { this.state.parts.length > 0 && <ListBlock name="spotify" handler={this.handleRemoveRow} list={this.state.parts}/> }
                <tbody>
                    <tr>
                        <td colSpan="2" className="center-text ui-text text-no-select" style={{fontStyle: "italic"}}>
                            <br></br>spotify playlist can be the name of either your own created playlist or one you follow, names are case sensitive
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <input type="text"
                                name="newPlaylistName" 
                                className="full-width" 
                                value={this.state.newPlaylistName} 
                                onChange={this.handleInputChange}
                                placeholder="spotify playlist name"></input>
                        </td>
                        <td>
                            <button className="button full-width" onClick={this.handleAddPart}>add</button>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <select name="newPlaylistReference" 
                                    className="full-width"
                                    value={this.state.newPlaylistReference}
                                    onChange={this.handleInputChange}>
                                { this.state.playlists
                                    .filter((entry) => entry.name != this.state.name)
                                    .map((entry) => <ReferenceEntry name={entry.name} key={entry.name} />) }
                            </select>
                        </td>
                        <td>
                            <button className="button full-width" onClick={this.handleAddReference}>add</button>
                        </td>
                    </tr>
                    <tr>
                        <td className="center-text ui-text text-no-select">
                            shuffle output?
                        </td>
                        <td>
                            <input type="checkbox"
                                name="shuffle"
                                checked={this.state.shuffle}
                                onChange={this.handleShuffleChange}></input>
                        </td>
                    </tr>
                    <tr>
                        <td className="center-text ui-text text-no-select">
                            include recommendations?
                        </td>
                        <td>
                            <input type="checkbox"
                                name="include_recommendations"
                                checked={this.state.include_recommendations}
                                onChange={this.handleRecChange}></input>
                        </td>
                    </tr>
                    <tr>
                        <td className="center-text ui-text text-no-select">
                            number of recommendations
                        </td>
                        <td>
                        <input type="number" 
                                name="recommendation_sample"
                                className="full-width"
                                value={this.state.recommendation_sample}
                                onChange={this.handleInputChange}></input>
                        </td>
                    </tr>
                    { this.state.type == 'recents' &&
                    <tr>
                        <td className="center-text ui-text text-no-select">
                            added since (days)
                        </td>
                        <td>
                            <input type="number" 
                                name="day_boundary"
                                className="full-width"
                                value={this.state.day_boundary}
                                onChange={this.handleInputChange}></input>
                        </td>
                    </tr>
                    }
                    <tr>
                        <td className="center-text ui-text text-no-select">
                            playlist type
                        </td>
                        <td>
                            <select className="full-width" 
                                    name="type" 
                                    onChange={this.handleInputChange}
                                    value={this.state.type}>
                                <option value="default">default</option>
                                <option value="recents">recents</option>
                            </select>
                        </td>
                    </tr>
                    { this.state.type == 'recents' &&
                    <tr>
                        <td colSpan="2" className="center-text ui-text text-no-select" style={{fontStyle: "italic"}}>
                            <br></br>'recents' playlists search for and include this months and last months playlists when named in the format
                            <br></br>[month] [year]
                            <br></br>e.g july 19 (lowercase)
                        </td>
                    </tr>
                    }
                    <tr>
                        <td colSpan="2">
                            <button className="button full-width" onClick={this.handleRun}>play</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        );

        const error = <p style={{textAlign: "center"}}>{ this.state.error_text }</p>;

        return this.state.error ? error : table;
    }

}

function ReferenceEntry(props) {
    return (
        <option value={props.name}>{props.name}</option>
    );
}

function ListBlock(props) {
    return (
        <tbody>
            <tr><td colSpan="2" className="ui-text center-text text-no-select" style={{fontStyle: 'italic'}}>{props.name}</td></tr>
            { props.list.map((part) => <Row part={ part } key={ part } handler={props.handler}/>) }
        </tbody>
    );
}

function Row (props) {
    return (
        <tr>
            <td className="ui-text center-text text-no-select">{ props.part }</td>
            <td><button className="ui-text center-text button full-width" onClick={(e) => props.handler(props.part, e)}>remove</button></td>
        </tr>
    );
}

export default ScratchView;