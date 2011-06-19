//
//  SLTableItemCell.m
//  shoppleyClient
//
//  Created by yod on 6/17/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLTableItemCell.h"

#import <Three20Core/NSDateAdditions.h>
#import <Three20Style/UIFontAdditions.h>
#import <Three20UI/UIViewAdditions.h>

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
        self.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
        self.selectionStyle = TTSTYLEVAR(tableSelectionStyle);
        
        SLCurrentOfferTableItem* item = object;
        SLCurrentOffer* offer = item.offer;
        
        if (offer.name.length) {
            self.titleLabel.text = offer.name;
        }
        if (offer.name.length) {
            self.captionLabel.text = [NSString stringWithFormat:@"by %@", offer.merchantName];
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

@implementation SLRightValueTableItemCell

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString*)identifier {
    if ((self = [super initWithStyle:style reuseIdentifier:identifier])) {
        self.textLabel.font = TTSTYLEVAR(tableSmallFont);
        
        self.detailTextLabel.lineBreakMode = UILineBreakModeTailTruncation;
        self.detailTextLabel.numberOfLines = 1;
    }
    
    return self;
}

+ (CGFloat)tableView:(UITableView*)tableView rowHeightForObject:(id)object {
    return 42;
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    static CGFloat kValueWidth = 75;
    static CGFloat kValueSpacing = 12;
    
    CGFloat valueWidth = self.contentView.width - (kTableCellHPadding*2 + kValueWidth + kValueSpacing);
    //CGFloat innerHeight = self.contentView.height - kTableCellVPadding*2;
    
    self.textLabel.frame = CGRectMake(kTableCellHPadding + kValueSpacing + valueWidth, self.contentView.height - kTableCellVPadding - self.textLabel.font.ttLineHeight, kValueWidth, self.textLabel.font.ttLineHeight);
    self.detailTextLabel.frame = CGRectMake(kTableCellHPadding, self.contentView.height - kTableCellVPadding - self.detailTextLabel.font.ttLineHeight, valueWidth, self.detailTextLabel.font.ttLineHeight);
}

@end
