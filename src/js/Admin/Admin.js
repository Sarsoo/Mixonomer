import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link } from "react-router-dom";
const axios = require('axios');

import Lock from "./Lock.js";

class Admin extends Component {
    render(){
        return (
            <div>
                <ul className="navbar" style={{width: "100%"}}>
                    <li><Link to={`${this.props.match.url}/lock`}>lock accounts</Link></li>
                </ul>

                <Route path={`${this.props.match.url}/lock`} component={Lock} />

            </div>
        );
    }
}

export default Admin