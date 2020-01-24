import React, { Component } from "react";
const axios = require('axios');

import showMessage from "../Toast.js"

var thisMonth = [
    'january',
    'february',
    'march',
    'april',
    'may',
    'june',
    'july',
    'august',
    'septempber',
    'october',
    'november',
    'december'
];

var lastMonth = [
    'december',
    'january',
    'february',
    'march',
    'april',
    'may',
    'june',
    'july',
    'august',
    'septempber',
    'october',
    'november'
];

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
            newReferenceName: '',

            shuffle: false,
            include_recommendations: false,
            add_this_month: false,
            add_last_month: false
        }
        this.handleAddPart = this.handleAddPart.bind(this);
        this.handleAddReference = this.handleAddReference.bind(this);
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleRemovePart = this.handleRemovePart.bind(this);
        this.handleRemoveReference = this.handleRemoveReference.bind(this);

        this.handleRun = this.handleRun.bind(this);

        this.handleShuffleChange = this.handleShuffleChange.bind(this);
        this.handleIncludeRecommendationsChange = this.handleIncludeRecommendationsChange.bind(this);
        this.handleThisMonthChange = this.handleThisMonthChange.bind(this);
        this.handleLastMonthChange = this.handleLastMonthChange.bind(this);
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
                newReferenceName: filteredPlaylists.length > 0 ? filteredPlaylists[0].name : ''
            });
        })
        .catch((error) => {
            showMessage(`Error Getting Playlists (${error.response.status})`);
        });
    }

    handleInputChange(event){
        this.setState({
            [event.target.name]: event.target.value
        });
    }

    handleShuffleChange(event) {
        this.setState({
            shuffle: event.target.checked
        });
    }

    handleThisMonthChange(event) {
        this.setState({
            add_this_month: event.target.checked
        });
    }

    handleLastMonthChange(event) {
        this.setState({
            add_last_month: event.target.checked
        });
    }

    handleIncludeRecommendationsChange(event) {
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
                showMessage('Playlist Already Added');  
            }

        }else{
            showMessage('Enter Playlist Name');
        }
    }

    handleAddReference(event){

        if(this.state.newReferenceName.length != 0){
            
            var check = this.state.playlist_references.includes(this.state.newReferenceName);

            if(check == false) {
                var playlist_references = this.state.playlist_references.slice();
                playlist_references.push(this.state.newReferenceName);
                
                playlist_references.sort(function(a, b){
                    if(a < b) { return -1; }
                    if(a > b) { return 1; }
                    return 0;
                });

                var filteredPlaylists = this.state.playlists.filter((entry) => entry.name != this.state.name);
                
                this.setState({
                    playlist_references: playlist_references,
                    newReferenceName: filteredPlaylists.length > 0 ? filteredPlaylists[0].name : ''
                });

            }else{
                showMessage('Playlist Already Added');  
            }

        }else{
            showMessage('No Other Playlists To Add');   
        }
    }

    handleRemovePart(id, event){
        var parts = this.state.parts;
        parts = parts.filter(e => e !== id);
        this.setState({
            parts: parts
        });

        if(parts.length == 0) {
            parts = -1;
        }
    }

    handleRemoveReference(id, event){
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
                        playlist_type: this.state.type,
                        add_this_month: this.state.add_this_month,
                        add_last_month: this.state.add_last_month
                    })
                    .then((reponse) => {
                        showMessage(`Played`);
                    })
                    .catch((error) => {
                        showMessage(`Error Playing (${error.response.status})`);
                    });
                }else{
                    showMessage(`Link Spotify Before Running`);
                }
            }).catch((error) => {
                showMessage(`Error Playing (${error.response.status})`);
            });
        }else{
            showMessage(`Add Either Playlists Or Parts`);
        }
    }

    render(){

        var date = new Date();

        const table = (
            <table className="app-table max-width">
                {/* <thead>
                    <tr>
                        <th colSpan="2"><h1 className="text-no-select">{ this.state.name }</h1></th>
                    </tr>
                </thead> */}
                { this.state.playlist_references.length > 0 && <ListBlock name="managed" handler={this.handleRemoveReference} list={this.state.playlist_references}/> }
                { this.state.parts.length > 0 && <ListBlock name="spotify" handler={this.handleRemovePart} list={this.state.parts}/> }
                <tbody>
                    <tr>
                        <td colSpan="2" className="center-text ui-text text-no-select" style={{fontStyle: "italic"}}>
                            <br></br>Spotify playlist can be the name of either your own created playlist or one you follow, names are case sensitive
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <input type="text"
                                name="newPlaylistName" 
                                className="full-width" 
                                value={this.state.newPlaylistName} 
                                onChange={this.handleInputChange}
                                placeholder="Spotify Playlist Name"></input>
                        </td>
                        <td>
                            <button className="button full-width" onClick={this.handleAddPart}>Add</button>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <select name="newReferenceName" 
                                    className="full-width"
                                    value={this.state.newReferenceName}
                                    onChange={this.handleInputChange}>
                                { this.state.playlists
                                    .filter((entry) => entry.name != this.state.name)
                                    .map((entry) => <ReferenceEntry name={entry.name} key={entry.name} />) }
                            </select>
                        </td>
                        <td>
                            <button className="button full-width" onClick={this.handleAddReference}>Add</button>
                        </td>
                    </tr>
                    <tr>
                        <td className="center-text ui-text text-no-select">
                            Shuffle Output
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
                            Include Recommendations
                        </td>
                        <td>
                            <input type="checkbox"
                                name="include_recommendations"
                                checked={this.state.include_recommendations}
                                onChange={this.handleIncludeRecommendationsChange}></input>
                        </td>
                    </tr>
                    <tr>
                        <td className="center-text ui-text text-no-select">
                            Recommendation Size
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
                            Added Since (Days)
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
                    { this.state.type == 'recents' &&
                    <tr>
                        <td className="center-text ui-text text-no-select">
                            Include {thisMonth[date.getMonth()]} Playlist
                        </td>
                        <td>
                            <input type="checkbox" 
                                checked={this.state.add_this_month}
                                onChange={this.handleThisMonthChange}></input>
                        </td>
                    </tr>
                    }
                    { this.state.type == 'recents' &&
                    <tr>
                        <td className="center-text ui-text text-no-select">
                            Include {lastMonth[date.getMonth()]} Playlist
                        </td>
                        <td>
                            <input type="checkbox" 
                                checked={this.state.add_last_month}
                                onChange={this.handleLastMonthChange}></input>
                        </td>
                    </tr>
                    }
                    <tr>
                        <td className="center-text ui-text text-no-select">
                            Type
                        </td>
                        <td>
                            <select className="full-width" 
                                    name="type" 
                                    onChange={this.handleInputChange}
                                    value={this.state.type}>
                                <option value="default">Default</option>
                                <option value="recents">Recents</option>
                            </select>
                        </td>
                    </tr>
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
            <td><button className="ui-text center-text button full-width" onClick={(e) => props.handler(props.part, e)}>Remove</button></td>
        </tr>
    );
}

export default ScratchView;