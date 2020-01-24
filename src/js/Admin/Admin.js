import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link } from "react-router-dom";
const axios = require('axios');

import Lock from "./Lock.js";
import Functions from "./Functions.js";
import Tasks from "./Tasks.js";

class Admin extends Component {
    render(){
        return (
            <div>
                <ul className="navbar" style={{width: "100%"}}>
                    <li><Link to={`${this.props.match.url}/lock`}>Lock Accounts</Link></li>
                    <li><Link to={`${this.props.match.url}/functions`}>Functions</Link></li>
                    <li><Link to={`${this.props.match.url}/tasks`}>Tasks</Link></li>
                </ul>

                <Route path={`${this.props.match.url}/lock`} component={Lock} />
                <Route path={`${this.props.match.url}/functions`} component={Functions} />
                <Route path={`${this.props.match.url}/tasks`} component={Tasks} />

            </div>
        );
    }
}

export default Admin