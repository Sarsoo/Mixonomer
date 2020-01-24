import React, { Component } from "react";
const axios = require('axios');

class Index extends Component{

    constructor(props){
        super(props);
        this.state = {}
    }

    render(){
        return (
            <table className="app-table">
                <thead>
                    <tr>
                        <th>
                            <h1 className="center-text text-no-select">Music Tools</h1>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td className="center-text text-no-select ui-text" style={{fontSize: "20px"}}>
                            Construct spotify playlists from selections of other playlists
                        </td>
                    </tr>
                    <tr>
                        <td className="center-text text-no-select ui-text">
                            Group sub-genre playlists
                        </td>
                    </tr>
                    <tr>
                        <td className="center-text text-no-select ui-text">
                            Optionally append auto-generated recommendations
                        </td>
                    </tr>
                    <tr>
                        <td className="center-text text-no-select ui-text">
                            <br></br>Playlists are run multiple times a day
                        </td>
                    </tr>
                </tbody>
            </table>
        );
    }
}

export default Index;