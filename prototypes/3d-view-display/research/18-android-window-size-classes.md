# Android Developers: Use window size classes

https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes

> Available width and height are classified separately, so at any point in time, your app has two window size classes---one for width, one for height.

> Available width is usually more important than available height due to the ubiquity of vertical scrolling, so the width window size class is likely more relevant to your app's UI.

From the table of breakpoints:

> Compact height | height < 480dp | 99.78% of phones in landscape

> Medium height | 480dp ≤ height < 900dp | 96.56% of tablets in landscape, 97.59% of phones in portrait

> **Note:** Most apps can build an adaptive UI by considering only the width window size class. However, also consider the height window size class for scenarios such as phones or open flippables in landscape orientation; the window width is typically medium, but window height is compact, in which case two pane layouts are not practical.

> window size classes are determined by the window size available to your application regardless of the type of device the app is running on
