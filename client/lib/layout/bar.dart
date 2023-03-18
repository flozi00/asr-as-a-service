import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

Widget build_app_bar(
    BuildContext context, List<Tab> tabs, List<Widget> children) {
  List<Widget> views = [
    for (Widget child in children)
      // Create a container for each child
      Container(
        // Set constraints for each container
        constraints: BoxConstraints(
            minWidth: 5,
            maxWidth: 512,
            maxHeight: MediaQuery.of(context).size.height - 200),
        // Set padding for each container
        padding: const EdgeInsets.fromLTRB(25, 55, 25, 10),
        // Set alignment for each container
        alignment: Alignment.center,
        // Wrap each child in a SingleChildScrollView to enable scrolling
        child: child,
      )
  ];

  return DefaultTabController(
      length: children.length,
      child: Scaffold(
        body: NestedScrollView(
          headerSliverBuilder: (BuildContext context, bool innerBoxIsScrolled) {
            return <Widget>[
              SliverAppBar(
                floating: true,
                pinned: true,
                stretch: false,
                actions: [
                  IconButton(
                      onPressed: () {
                        launchUrl(Uri.parse("https://a-ware.io/atra"));
                      },
                      icon: const Icon(Icons.help_outline))
                ],
              ),
              /*SliverPersistentHeader(
                delegate: _SliverAppBarDelegate(
                  TabBar(
                    indicatorSize: TabBarIndicatorSize.label,
                    tabs: tabs,
                  ),
                ),
                pinned: false,
                floating: false,
              ),*/
            ];
          },
          body: TabBarView(
            physics: const BouncingScrollPhysics(),
            children: views,
          ),
        ),
      ));
}

class _SliverAppBarDelegate extends SliverPersistentHeaderDelegate {
  // Declare the instance variable for the TabBar
  _SliverAppBarDelegate(this._tabBar);

  // Define the TabBar variable
  final TabBar _tabBar;

  // Define the minimum height of the header
  @override
  double get minExtent => _tabBar.preferredSize.height;
  // Define the maximum height of the header
  @override
  double get maxExtent => _tabBar.preferredSize.height;

  // Build the header
  @override
  Widget build(
      BuildContext context, double shrinkOffset, bool overlapsContent) {
    // Return the TabBar
    return _tabBar;
  }

  // When should the header rebuild?
  @override
  bool shouldRebuild(_SliverAppBarDelegate oldDelegate) {
    return false;
  }
}
