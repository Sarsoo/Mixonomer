import React, { Component } from "react";
import { Route, Link, Switch } from "react-router-dom";
import { Paper, Tabs, Tab} from '@material-ui/core';


import Lock from "./Lock.js";
import Functions from "./Functions.js";
import Tasks from "./Tasks.js";

class Admin extends Component {

    constructor(props){
        super(props);
        this.state = {
            tab: 0
        }
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(e, newValue){
        this.setState({
            tab: newValue
        });
    }

    render(){
        return (
            <div>
            <Paper>
                <Tabs
                    value={this.state.tab}
                    onChange={this.handleChange}
                    indicatorColor="primary"
                    centered
                    width="50%"
                >
                    <Tab label="Lock Accounts" component={Link} to={`${this.props.match.url}/lock`} />
                    <Tab label="Functions" component={Link} to={`${this.props.match.url}/functions`} />
                    <Tab label="Tasks" component={Link} to={`${this.props.match.url}/tasks`} />
                </Tabs>
            </Paper>
            <Switch>
                <Route path={`${this.props.match.url}/lock`} component={Lock} />
                <Route path={`${this.props.match.url}/functions`} component={Functions} />
                <Route path={`${this.props.match.url}/tasks`} component={Tasks} />
            </Switch>
            </div>
        );
    }
}

export default Admin