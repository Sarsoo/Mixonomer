import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link, Switch, Redirect} from "react-router-dom";

import Index from "./Index/Index.js";
import Maths from "./Maths/Maths.js";
import Playlists from "./Playlist/Playlists.js";
import PlaylistView from "./Playlist/View/View.js";
import Settings from "./Settings/Settings.js";
import Admin from "./Admin/Admin.js";

import NotFound from "./Error/NotFound.js";

import showMessage from "./Toast.js"

import GlobalTheme from './Theme.js';

import { Typography } from '@material-ui/core';
import { ThemeProvider } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';

import Drawer from '@material-ui/core/Drawer';
import List from '@material-ui/core/List';
import Divider from '@material-ui/core/Divider';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import HomeIcon from '@material-ui/icons/Home';
import { Build, PieChart, QueueMusic, ExitToApp, AccountCircle, KeyboardBackspace } from '@material-ui/icons'

const axios = require('axios');

class MusicTools extends Component {

    constructor(props){
        super(props);
        this.state = {
            type: null,
            spotify_linked: null,
            drawerOpen: false
        }
        this.setOpen = this.setOpen.bind(this);
    }

    componentDidMount() {
        this.getUserInfo();
    }

    componentWillUnmount() {
        this.userInfoCancelToken.cancel();
    }

    getUserInfo(){
        this.userInfoCancelToken = axios.CancelToken.source();

        var self = this;
        axios.get('/api/user', {
            cancelToken: this.userInfoCancelToken.token
        })
        .then((response) => {
            self.setState({
                type: response.data.type,
                spotify_linked: response.data.spotify_linked
            })
        })
        .catch((error) => {
            showMessage(`error getting user info (${error.response.status})`);
        });
    }

    setOpen(bool){
        this.setState({
            drawerOpen: bool
        })
    }

    render(){
        return (
            <Router>
                <div className="card pad-12">
                <ThemeProvider theme={GlobalTheme}>
                    <AppBar position="static">
                    <Toolbar>
                        <IconButton edge="start" color="inherit" aria-label="menu" onClick={(e) => this.setOpen(true)}>
                        <MenuIcon />
                        </IconButton>
                        <Typography variant="h6">
                            Music Tools
                        </Typography>
                    </Toolbar>
                    </AppBar>
                    <Drawer
                        variant="persistent"
                        anchor="left"
                        open={this.state.drawerOpen}
                    >
                        <div>
                        <IconButton onClick={(e) => this.setOpen(false)}>
                            <ChevronLeftIcon />
                        </IconButton>
                        </div>
                        <Divider />
                        <List>
                            <ListItem button key="home" component={Link} to='/app'>
                                <ListItemIcon><HomeIcon /></ListItemIcon>
                                <ListItemText primary="Home" />
                            </ListItem>
                            <ListItem button key="playlists" component={Link} to='/app/playlists'>
                                <ListItemIcon><QueueMusic /></ListItemIcon>
                                <ListItemText primary="Playlists" />
                            </ListItem>
                            <ListItem button key="maths" component={Link} to='/app/maths/count'>
                                <ListItemIcon><PieChart /></ListItemIcon>
                                <ListItemText primary="Maths" />
                            </ListItem>
                            <ListItem button key="settings" component={Link} to='/app/settings/password'>
                                <ListItemIcon><Build /></ListItemIcon>
                                <ListItemText primary="Settings" />
                            </ListItem>
                            { this.state.type == 'admin' &&
                                <ListItem button key="admin" component={Link} to='/app/admin/lock'>
                                    <ListItemIcon><AccountCircle /></ListItemIcon>
                                    <ListItemText primary="Admin" />
                                </ListItem>
                            }
                            <ListItem button key="logout" component={Link} to='/auth/logout'>
                                <ListItemIcon><KeyboardBackspace /></ListItemIcon>
                                <ListItemText primary="Logout" />
                            </ListItem>
                            <ListItem button key="sarsoo.xyz" component={Link} to='https://sarsoo.xyz'>
                                <ListItemIcon><ExitToApp /></ListItemIcon>
                                <ListItemText primary="sarsoo.xyz" />
                            </ListItem>
                        </List>
                    </Drawer>
                </ThemeProvider>
                    <div className="pad-12">
                        <Switch>
                            <Route path="/app" exact component={Index} />
                            <Route path="/app/playlists" component={Playlists} />
                            <Route path="/app/maths" component={Maths} />
                            <Route path="/app/settings" component={Settings} />
                            { this.state.type == 'admin' && <Route path="/app/admin" component={Admin} /> }
                            <Route path='/app/playlist/:name' component={PlaylistView} />
                            <Route component={NotFound} />
                        </Switch>
                    </div>
                </div>
                <footer>
                    <a href="https://github.com/Sarsoo/spotify-web">view source code</a>
                </footer>
            </Router>
        );
    }

}

export default MusicTools;