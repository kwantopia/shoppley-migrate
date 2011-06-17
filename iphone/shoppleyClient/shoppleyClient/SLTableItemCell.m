//
//  SLTableItemCell.m
//  shoppleyClient
//
//  Created by yod on 6/17/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLTableItemCell.h"

#import <Three20Core/NSDateAdditions.h>

#import "SLCurrentOffer.h"

@implementation SLCurrentOfferTableItemCell

+ (CGFloat)tableView:(UITableView*)tableView rowHeightForObject:(id)object {
    // TODO(yod): fix this
    /*
    SLCurrentOfferTableItem* item = object;
    SLCurrentOffer* offer = item.offer;
    */
    return 90;
}

- (void)setObject:(id)object {
    if (_item != object) {
        SLCurrentOfferTableItem* item = object;
        
        // Copy from TTTableLinkedItemCell.m
        if (item.URL) {
            TTNavigationMode navigationMode = [[TTNavigator navigator].URLMap
                                               navigationModeForURL:item.URL];
            if (item.accessoryURL) {
                self.accessoryType = UITableViewCellAccessoryDetailDisclosureButton;
                
            } else if (navigationMode == TTNavigationModeCreate ||
                       navigationMode == TTNavigationModeShare) {
                self.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
                
            } else {
                self.accessoryType = UITableViewCellAccessoryNone;
            }
            
            self.selectionStyle = TTSTYLEVAR(tableSelectionStyle);
            
        } else if (nil != item.delegate && nil != item.selector) {
            self.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
            self.selectionStyle = TTSTYLEVAR(tableSelectionStyle);
            
        } else {
            self.accessoryType = UITableViewCellAccessoryNone;
            self.selectionStyle = UITableViewCellSelectionStyleNone;
        }
        
        SLCurrentOffer* offer = item.offer;
        
        if (offer.name.length) {
            self.titleLabel.text = offer.merchantName;
        }
        if (offer.name.length) {
            self.captionLabel.text = offer.name;
        }
        if (offer.name.length) {
            self.detailTextLabel.text = offer.description;
        }
        if (offer.name.length) {
            self.timestampLabel.text = offer.expires;
            //self.timestampLabel.text = [item.timestamp formatShortTime];
        }
        if (offer.img) {
            self.imageView2.urlPath = offer.img;
        }
    }
}

- (UILabel*)timestampLabel {
    if (!_timestampLabel) {
        _timestampLabel = [[UILabel alloc] init];
        _timestampLabel.font = TTSTYLEVAR(tableTimestampFont);
        _timestampLabel.textColor = [UIColor redColor];
        _timestampLabel.highlightedTextColor = [UIColor whiteColor];
        _timestampLabel.contentMode = UIViewContentModeLeft;
        [self.contentView addSubview:_timestampLabel];
    }
    return _timestampLabel;
}

@end
