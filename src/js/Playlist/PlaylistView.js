import React, { Component } from "react";
const axios = require('axios');

class PlaylistView extends Component{

    constructor(props){
        super(props);
        console.log(this.props.match.params.name);
        this.state = {
            name: this.props.match.params.name,
            parts: [],
            error: false,
            error_text: null,
            add_part_value: ''
        }
        this.handleAddPart = this.handleAddPart.bind(this);
        this.handleAddPartChange = this.handleAddPartChange.bind(this);
    }

    componentDidMount(){
        this.getPlaylistInfo();
    }

    getPlaylistInfo(){
        axios.get(`/api/playlist?name=${ this.state.name }`)
            .then((response) => {
                this.setState(response.data);
            }).catch((error) => {
                this.setState({
                    error: true,
                    error_text: "error pulling playlist info"
                });
            });
    }

    handleAddPartChange(event){
        this.setState({
            add_part_value: event.target.value
        });
    }

    handleAddPart(event){
        var parts = this.state.parts;
        parts.push(this.state.add_part_value);
        this.setState({
            parts: parts
        });
        axios.post('/api/playlist', {
            name: this.state.name,
            parts: parts
        }).then((response) => {
            console.log(reponse);
        }).catch((error) => {
            console.log(error);
        });
    }

    render(){

        const table = (
            <table className="app-table max-width">
                <thead>
                    <tr>
                        <th colSpan="2"><h1>{ this.state.name }</h1></th>
                    </tr>
                </thead>
                <tbody>
                    { this.state.parts.map((part) => <Row part={ part } key={ part }/>) }
                    <tr>
                        <td>
                            <input type="text" className="full-width" value={this.state.add_part_value} onChange={this.handleAddPartChange}></input>
                        </td>
                        <td>
                            <button className="button full-width" onClick={this.handleAddPart}>add</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        );

        const error = <p style={{textAlign: "center"}}>{ this.state.error_text }</p>;

        return this.state.error ? error : table;
    }

}

function Row (props) {
    return (
        <tr>
            <td className="ui-text center-text">{ props.part }</td>
            <td className="ui-text center-text">remove</td>
        </tr>
    );
}

export default PlaylistView;